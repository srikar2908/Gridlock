from typing import Any, Dict

import httpx

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.schemas.requests import CopilotRequest

logger = get_logger(__name__)


class CopilotService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def answer(self, request: CopilotRequest) -> dict:
        analysis = request.analysis or {}
        return await self.explain(analysis=analysis, question=request.question)

    async def explain(self, analysis: Dict[str, Any], question: str = "Explain this traffic incident decision.") -> dict:
        priority = analysis.get("priority", {})
        closure = analysis.get("closure_prediction", {})
        clearance = analysis.get("clearance", {})
        resources = analysis.get("resources", {})
        similar = analysis.get("similar_incidents", [])
        causes = analysis.get("causes", [])
        recommended = analysis.get("recommended_actions", [])
        fallback = (
            f"Current operational read: priority is {priority.get('priority_level', 'unknown')} "
            f"and closure_required is {closure.get('closure_required', 'unknown')}. "
            f"Recommended next step: {recommended[0] if recommended else 'validate the incident and retrieve similar cases'}."
        )
        if not self.settings.groq_api_key:
            return self._structured_fallback(fallback, priority, closure, clearance, resources, recommended)

        prompt = {
            "question": question,
            "current_predictions": analysis,
            "instruction": (
                "Explain the ML decisions for traffic operators. Do not change predictions. "
                "Return concise sections: Incident Summary, Risk Assessment, Officer Briefing, "
                "Recommended Actions, Explanation Cards."
            ),
        }
        for model in [self.settings.groq_primary_model, self.settings.groq_fallback_model]:
            try:
                content = await self._call_groq(model, prompt)
                return {
                    "mode": "groq_rag",
                    "model": model,
                    "incident_summary": content,
                    "risk_assessment": f"Priority: {priority.get('priority_level')} ({priority.get('priority_score')})",
                    "officer_briefing": self._briefing(resources, clearance),
                    "recommended_actions": recommended,
                    "explanation_cards": self._cards(priority, closure, clearance, resources, similar, causes),
                }
            except Exception as exc:
                logger.warning("Groq model %s failed: %s", model, exc)
        return self._structured_fallback(fallback, priority, closure, clearance, resources, recommended)

    async def _call_groq(self, model: str, prompt: dict) -> str:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a traffic operations copilot explaining ML decisions."},
                        {"role": "user", "content": str(prompt)},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _structured_fallback(self, answer, priority, closure, clearance, resources, recommended) -> dict:
        return {
            "mode": "rule_based_rag",
            "model": None,
            "incident_summary": answer,
            "risk_assessment": f"Priority: {priority.get('priority_level', 'unknown')}",
            "officer_briefing": self._briefing(resources, clearance),
            "recommended_actions": recommended,
            "explanation_cards": self._cards(priority, closure, clearance, resources, [], []),
            "sources": ["current_prediction_results", "similar_incidents", "knowledge_base"],
        }

    @staticmethod
    def _briefing(resources: dict, clearance: dict) -> str:
        return (
            f"Stage {resources.get('officers', 0)} officers, {resources.get('traffic_units', 0)} traffic units, "
            f"and {resources.get('tow_trucks', 0)} tow trucks. Estimated clearance is "
            f"{clearance.get('estimated_minutes', 'unknown')} minutes."
        )

    @staticmethod
    def _cards(priority, closure, clearance, resources, similar, causes) -> list[dict]:
        return [
            {"title": "Why this priority?", "explanation": f"Priority is driven by event, corridor, zone, and severity factors: {priority.get('factors', {})}."},
            {"title": "Why this closure decision?", "explanation": f"Closure required is {closure.get('closure_required')} with confidence {closure.get('confidence')}."},
            {"title": "Why this clearance estimate?", "explanation": f"Clearance uses {clearance.get('basis', 'retrieval')} evidence and similar incident history."},
            {"title": "Why these resources?", "explanation": f"Resources match priority, clearance duration, and event type: {resources}."},
        ]
