import json
import re
from typing import Any, Dict, List

import httpx

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.schemas.requests import CopilotRequest

logger = get_logger(__name__)


class CopilotService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def answer(self, request: CopilotRequest) -> dict:
        return await self.explain(analysis=request.analysis or {}, question=request.question)

    async def explain(self, analysis: Dict[str, Any], question: str = "Explain this traffic incident decision.") -> dict:
        priority = analysis.get("priority", {})
        closure = analysis.get("closure_prediction", {})
        clearance = analysis.get("clearance", {})
        resources = analysis.get("resources", {})
        similar = analysis.get("similar_incidents", [])
        causes = analysis.get("causes", [])
        recommended = analysis.get("recommended_actions", [])

        grounded = self._grounded_response(priority, closure, clearance, resources, similar, causes, recommended)
        if not self.settings.groq_api_key:
            return grounded

        llm_context = self._llm_context(priority, closure, clearance, resources, similar, recommended)
        prompt = self._llm_prompt(llm_context, question)
        for model in [self.settings.groq_primary_model, self.settings.groq_fallback_model]:
            try:
                content = await self._call_groq(model, prompt)
                parsed_content = self._parse_llm_json(content)
                grounded["mode"] = "groq_grounded_rag"
                grounded["model"] = model
                grounded["llm_context"] = llm_context
                grounded["llm_raw_response"] = content
                accepted, rejection_reason = self._check_guardrails(content, priority, closure, clearance, resources)
                if accepted:
                    grounded["llm_brief"] = parsed_content or content
                    grounded["llm_status"] = "accepted"
                else:
                    grounded["llm_status"] = "rejected_by_grounding_guardrails"
                    grounded["llm_rejection_reason"] = rejection_reason
                    logger.warning(
                        "Copilot response rejected by guardrails: %s",
                        rejection_reason,
                    )
                    logger.warning(
                        "Rejected Groq response: %s",
                        content,
                    )
                grounded["confidence_note"] = "Visible command brief is deterministic. Groq is never allowed to change predictions or resources."
                return grounded
            except Exception as exc:
                logger.warning("Groq model %s failed: %s", model, exc)
        return grounded

    async def _call_groq(self, model: str, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.settings.groq_timeout_seconds) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a Bengaluru traffic operations copilot. "
                                "Return only valid JSON. Do not repeat numbers, invent facts, or modify predictions."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 420,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    @staticmethod
    def _llm_context(priority, closure, clearance, resources, similar, recommended) -> dict:
        similar_count = len(similar or [])
        clearance_values = [
            float(item.get("clearance_time"))
            for item in similar or []
            if item.get("clearance_time") is not None
        ]
        if clearance_values:
            historical_summary = (
                f"{similar_count} similar incidents reviewed. "
                f"Median clearance {round(sorted(clearance_values)[len(clearance_values) // 2], 1)} minutes."
            )
        else:
            historical_summary = "No similar incident history available."

        return {
            "incident_summary": "Current traffic incident under command-center review.",
            "priority_summary": f"{str(priority.get('priority_level', 'unknown')).title()} ({priority.get('priority_score', 'unknown')})",
            "closure_summary": (
                f"{'Required' if closure.get('closure_required') else 'Not required'} "
                f"({round(float(closure.get('confidence', 0) or 0) * 100)}% confidence)"
            ),
            "clearance_summary": f"{clearance.get('estimated_minutes', 'unknown')} minutes",
            "resource_summary": (
                f"{resources.get('officers', 0)} officers; "
                f"{resources.get('tow_trucks', 0)} tow truck(s); "
                f"{resources.get('traffic_units', 0)} traffic unit(s); "
                f"{resources.get('ambulance_units', 0)} ambulance(s)."
            ),
            "historical_summary": historical_summary,
            "recommended_actions": list(recommended or [])[:4],
        }

    @staticmethod
    def _llm_prompt(context: dict, question: str) -> str:
        actions = "\n".join(f"- {action}" for action in context["recommended_actions"]) or "- Validate via CCTV or field unit."
        return (
            "Create a concise operational briefing for Bengaluru traffic operations.\n\n"
            "Rules:\n"
            "- Maximum 250 words.\n"
            "- Do not repeat numbers.\n"
            "- Do not invent values.\n"
            "- Do not modify predictions.\n"
            "- Explain WHY the recommendation was made.\n"
            "- Use simple operational language.\n\n"
            "Return JSON with exactly these keys:\n"
            "incident_summary, risk_assessment, resource_explanation, historical_context, commander_recommendation.\n\n"
            f"Question: {question}\n\n"
            "Verified context:\n"
            f"Incident: {context['incident_summary']}\n"
            f"Priority: {context['priority_summary']}\n"
            f"Closure: {context['closure_summary']}\n"
            f"Clearance: {context['clearance_summary']}\n"
            f"Resources: {context['resource_summary']}\n"
            f"Historical evidence: {context['historical_summary']}\n"
            "Actions:\n"
            f"{actions}\n"
        )

    @staticmethod
    def _parse_llm_json(content: str) -> dict | None:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if not match:
                return None
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return parsed if isinstance(parsed, dict) else None

    def _grounded_response(self, priority, closure, clearance, resources, similar, causes, recommended) -> dict:
        incident_summary = (
            f"{str(priority.get('priority_level', 'unknown')).title()} priority incident. "
            f"Closure required: {closure.get('closure_required', 'unknown')} "
            f"with confidence {closure.get('confidence', 'unknown')}."
        )
        return {
            "mode": "deterministic_grounded_rag",
            "model": None,
            "incident_summary": incident_summary,
            "risk_assessment": self._risk_assessment(priority, closure, clearance),
            "officer_briefing": self._briefing(resources, clearance),
            "resource_plan": self._resource_plan(resources),
            "recommended_actions": recommended,
            "explanation_cards": self._cards(priority, closure, clearance, resources, similar, causes),
            "similar_incident_summary": self._similar_summary(similar),
            "confidence_note": "Copilot explains verified ML/service outputs only; it does not create predictions or resource counts.",
            "commander_brief": self._commander_brief(priority, closure, clearance, resources, recommended),
            "sources": ["current_prediction_results", "similar_incidents", "knowledge_base", "resource_service"],
        }

    @staticmethod
    def _briefing(resources: dict, clearance: dict) -> str:
        officer_label = resources.get("officer_requirement") or f"{resources.get('officers', 0)} Officers"
        tow_label = resources.get("tow_truck_requirement") or f"{resources.get('tow_trucks', 0)} Tow Trucks"
        traffic_label = resources.get("traffic_unit_requirement") or f"{resources.get('traffic_units', 0)} Traffic Units"
        level = resources.get("resource_level", "Resource Requirement Unavailable")
        return (
            f"Stage {officer_label}, {tow_label}, and {traffic_label}. "
            f"{level}. Estimated clearance is {clearance.get('estimated_minutes', 'unknown')} minutes."
        )

    @staticmethod
    def _cards(priority, closure, clearance, resources, similar, causes) -> list[dict]:
        return [
            {
                "title": "Why this priority?",
                "explanation": f"Priority is {priority.get('priority_level')} from scoring factors {priority.get('factors', {})}.",
            },
            {
                "title": "Why this closure decision?",
                "explanation": f"Closure required is {closure.get('closure_required')} with confidence {closure.get('confidence')}.",
            },
            {
                "title": "Why this clearance estimate?",
                "explanation": (
                    f"Clearance is {clearance.get('estimated_minutes')} minutes using "
                    f"{clearance.get('basis', 'retrieval')} evidence and similar incident history."
                ),
            },
            {
                "title": "Why these resources?",
                "explanation": f"Resource plan is {resources.get('summary', resources)}. Rationale: {resources.get('rationale', [])}.",
            },
            {
                "title": "Historical signal",
                "explanation": f"Top similar incidents considered: {len(similar)}. Likely causes: {causes or ['not available']}.",
            },
        ]

    @staticmethod
    def _risk_assessment(priority: dict, closure: dict, clearance: dict) -> str:
        return (
            f"Priority {priority.get('priority_level', 'unknown')} ({priority.get('priority_score', 'unknown')}); "
            f"closure_required={closure.get('closure_required', 'unknown')}; "
            f"clearance_eta={clearance.get('estimated_minutes', 'unknown')} minutes."
        )

    @staticmethod
    def _resource_plan(resources: dict) -> List[str]:
        return [
            resources.get("officer_requirement", f"{resources.get('officers', 0)} Officers"),
            resources.get("tow_truck_requirement", f"{resources.get('tow_trucks', 0)} Tow Trucks"),
            resources.get("traffic_unit_requirement", f"{resources.get('traffic_units', 0)} Traffic Units"),
            resources.get("ambulance_requirement", f"{resources.get('ambulance_units', 0)} Ambulances"),
            resources.get("resource_level", "Resource Requirement Unavailable"),
        ]

    @staticmethod
    def _similar_summary(similar: list) -> str:
        if not similar:
            return "No similar incident evidence available."
        top = similar[0]
        return (
            f"Closest historical match {top.get('similar_incident_id')} had similarity "
            f"{top.get('similarity_score')} and clearance {top.get('clearance_time')} minutes."
        )

    @staticmethod
    def _commander_brief(priority: dict, closure: dict, clearance: dict, resources: dict, recommended: list) -> str:
        next_action = recommended[0] if recommended else "Validate the incident through field unit or CCTV."
        return (
            f"Command brief: Treat this as {priority.get('priority_level', 'unknown')} priority "
            f"(score {priority.get('priority_score', 'unknown')}). "
            f"Deploy {resources.get('summary', 'the computed resource plan')}. "
            f"Hold closure decision at {closure.get('closure_required', 'unknown')} "
            f"with confidence {closure.get('confidence', 'unknown')}. "
            f"Expected clearance is {clearance.get('estimated_minutes', 'unknown')} minutes. "
            f"Immediate next action: {next_action}"
        )

    @staticmethod
    def _check_guardrails(content: str, priority: dict, closure: dict, clearance: dict, resources: dict) -> tuple[bool, str | None]:
        parsed = CopilotService._parse_llm_json(content)
        if parsed:
            validation_parts = [
                str(parsed.get("incident_summary", "")),
                str(parsed.get("risk_assessment", "")),
                str(parsed.get("resource_explanation", "")),
                str(parsed.get("commander_recommendation", "")),
            ]
            text = " ".join(validation_parts).lower()
            clearance_text = " ".join(
                [
                    str(parsed.get("risk_assessment", "")),
                    str(parsed.get("commander_recommendation", "")),
                ]
            ).lower()
        else:
            text = content.lower()
            clearance_text = text
        expected_closure = bool(closure.get("closure_required"))
        if not expected_closure and CopilotService._asserts_closure_required(text):
            return False, "contradicts closure prediction: expected closure_required=False"
        if expected_closure and CopilotService._asserts_no_closure_required(text):
            return False, "contradicts closure prediction: expected closure_required=True"

        expected_priority = str(priority.get("priority_level", "")).lower()
        for match in re.finditer(r"\b(low|medium|high|critical)\s+priority\b", text):
            mentioned = match.group(1)
            if expected_priority and mentioned != expected_priority:
                return False, f"contradicts priority level: expected {expected_priority}, saw {mentioned}"

        count_checks = [
            ("officers", int(resources.get("officers", 0) or 0), r"(\d+)(?:\s*-\s*(\d+))?\s+officers?"),
            ("tow_trucks", int(resources.get("tow_trucks", 0) or 0), r"(\d+)(?:\s*-\s*(\d+))?\s+tow\s+trucks?"),
            ("traffic_units", int(resources.get("traffic_units", 0) or 0), r"(\d+)(?:\s*-\s*(\d+))?\s+traffic\s+units?"),
            ("ambulance_units", int(resources.get("ambulance_units", 0) or 0), r"(\d+)(?:\s*-\s*(\d+))?\s+ambulances?"),
        ]
        for label, expected, pattern in count_checks:
            for match in re.finditer(pattern, text):
                low = int(match.group(1))
                high = int(match.group(2) or match.group(1))
                if not (low <= expected <= high):
                    return False, f"contradicts {label}: expected {expected}, saw {low}-{high}"

        expected_clearance = float(clearance.get("estimated_minutes", 0) or 0)
        tolerance = max(15.0, expected_clearance * 0.25)
        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\b", clearance_text):
            mentioned = float(match.group(1))
            if expected_clearance and abs(mentioned - expected_clearance) > tolerance:
                return False, f"contradicts clearance estimate: expected {expected_clearance}, saw {mentioned}"

        return True, None

    @staticmethod
    def _asserts_closure_required(text: str) -> bool:
        negative_context = [
            "closure required: false",
            "closure_required=false",
            "closure_required: false",
            "closure is not required",
            "no closure required",
            "not require closure",
            "does not require closure",
        ]
        if any(phrase in text for phrase in negative_context):
            return False
        positive_claims = [
            r"\broad closure is required\b",
            r"\bclosure is required\b",
            r"\bclosure required: true\b",
            r"\bclosure_required=true\b",
            r"\brequires a road closure\b",
            r"\bfull closure is required\b",
            r"\bcomplete closure is required\b",
            r"\bmust close\b",
        ]
        return any(re.search(pattern, text) for pattern in positive_claims)

    @staticmethod
    def _asserts_no_closure_required(text: str) -> bool:
        negative_claims = [
            r"\bclosure is not required\b",
            r"\bno closure required\b",
            r"\bclosure required: false\b",
            r"\bclosure_required=false\b",
            r"\bdoes not require closure\b",
        ]
        return any(re.search(pattern, text) for pattern in negative_claims)
