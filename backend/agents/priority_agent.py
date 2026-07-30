"""
BuildWise AI — Priority Agent
Classifies complaint priority: Low/Medium/High/Critical/Emergency
"""
import json
import re
from agents.base_agent import BaseAgent


PRIORITY_PROMPT = """You are a building safety and maintenance priority classifier.

Complaint: {complaint}
Category: {category}
Severity Hints: {severity_hints}
Diagnosis: {diagnosis}

Classify the priority level. Consider:
- EMERGENCY: Fire, gas leak, electrical short circuit, elevator with people stuck, flooding, structural collapse risk
- CRITICAL: Major equipment failure, safety hazard, affects many people
- HIGH: Significant disruption, equipment malfunction, health risk
- MEDIUM: Moderate impact, can wait 24-48h
- LOW: Minor issue, scheduled maintenance

Respond in JSON:
{{
  "priority": "<emergency|critical|high|medium|low>",
  "is_emergency": <true|false>,
  "requires_evacuation": <true|false>,
  "reasoning": "<brief explanation>",
  "response_time_hours": <number>
}}

Only respond with JSON."""

EMERGENCY_KEYWORDS = [
    "fire", "smoke", "gas leak", "explosion", "collapse", "flood",
    "stuck in lift", "stuck in elevator", "electrical fire", "short circuit",
    "gas smell", "carbon monoxide", "structural failure", "people trapped",
    "ambulance", "emergency", "critical", "life threatening"
]


class PriorityAgent(BaseAgent):
    name = "priority"
    description = "Classifies complaint urgency: Low/Medium/High/Critical/Emergency"

    async def _execute(self, state: dict) -> dict:
        # Quick keyword check for emergency before calling LLM
        full_text = f"{state.get('complaint_title', '')} {state.get('complaint_text', '')} {state.get('extracted_severity_hints', '')}".lower()
        
        is_keyword_emergency = any(kw in full_text for kw in EMERGENCY_KEYWORDS)

        if is_keyword_emergency:
            state["priority"] = "emergency"
            state["is_emergency"] = True
            state["requires_evacuation"] = any(kw in full_text for kw in ["fire", "gas leak", "explosion", "collapse", "flood"])
            state["priority_reasoning"] = "Emergency keywords detected. Immediate response required."
            return state

        prompt = PRIORITY_PROMPT.format(
            complaint=f"{state.get('complaint_title', '')} — {state.get('complaint_text', '')}",
            category=state.get("extracted_category", state.get("category", "general")),
            severity_hints=state.get("extracted_severity_hints", "none"),
            diagnosis=state.get("diagnosis", ""),
        )

        response = await self._call_llm(prompt)
        parsed = self._parse_json(response)

        state["priority"] = parsed.get("priority", "medium")
        state["is_emergency"] = parsed.get("is_emergency", False)
        state["requires_evacuation"] = parsed.get("requires_evacuation", False)
        state["priority_reasoning"] = parsed.get("reasoning", "")

        return state

    def _parse_json(self, text: str) -> dict:
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}

    async def _fallback(self, state: dict) -> dict:
        text = f"{state.get('complaint_title', '')} {state.get('complaint_text', '')}".lower()
        category = state.get("extracted_category", "general")

        if category in ["fire_safety", "elevator"] and any(w in text for w in ["stuck", "failure", "not working", "stopped"]):
            state["priority"] = "critical"
            state["is_emergency"] = False
        elif category in ["electrical", "plumbing"] and any(w in text for w in ["major", "severe", "complete", "total"]):
            state["priority"] = "high"
            state["is_emergency"] = False
        else:
            state["priority"] = "medium"
            state["is_emergency"] = False

        state["requires_evacuation"] = False
        state["priority_reasoning"] = "Classified based on category and keywords."
        return state
