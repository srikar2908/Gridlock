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

        prompt = {
            "question": question,
            "verified_facts": grounded,
            "guardrails": [
                "Use only verified_facts.",
                "Do not invent locations, injuries, resource counts, causes, confidence, or clearance time.",
                "Do not override ML predictions.",
                "If information is missing, say it is not available.",
                "Keep it concise for a traffic command center.",
            ],
        }
        for model in [self.settings.groq_primary_model, self.settings.groq_fallback_model]:
            try:
                content = await self._call_groq(model, prompt)
                grounded["mode"] = "groq_grounded_rag"
                grounded["model"] = model
                if self._passes_guardrails(content, priority, closure, clearance, resources):
                    grounded["llm_brief"] = content
                    grounded["llm_status"] = "accepted_as_secondary_grounded_text"
                else:
                    grounded["llm_status"] = "rejected_by_grounding_guardrails"
                grounded["confidence_note"] = "Visible command brief is deterministic. Groq is never allowed to change predictions or resources."
                return grounded
            except Exception as exc:
                logger.warning("Groq model %s failed: %s", model, exc)
        return grounded

    async def _call_groq(self, model: str, prompt: dict) -> str:
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
                                "You are GRIDLOCK Traffic Operations Copilot. You explain verified ML outputs. "
                                "Never add new facts or change resource recommendations."
                            ),
                        },
                        {"role": "user", "content": str(prompt)},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 650,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

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
    def _passes_guardrails(content: str, priority: dict, closure: dict, clearance: dict, resources: dict) -> bool:
        text = content.lower()
        required_phrases = [
            str(priority.get("priority_level", "")).lower(),
            str(resources.get("officer_requirement", "")).lower(),
            str(resources.get("tow_truck_requirement", "")).lower(),
            str(resources.get("resource_level", "")).lower(),
            str(clearance.get("estimated_minutes", "")).lower(),
        ]
        if any(phrase and phrase not in text for phrase in required_phrases):
            return False
        forbidden_patterns = [
            "3 tow trucks",
            "4 tow trucks",
            "5 tow trucks",
            "6 tow trucks",
            "casualty",
            "fatality",
            "injured",
            "death",
        ]
        if any(pattern in text for pattern in forbidden_patterns):
            return False
        if "closure" in text and str(closure.get("closure_required")).lower() not in text:
            return False
        return True
