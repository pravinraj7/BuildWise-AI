"""
BuildWise AI — Complaint Understanding Agent
Extracts structured information from complaint text.
"""
import json
import re
from agents.base_agent import BaseAgent


UNDERSTANDING_PROMPT = """You are a building maintenance complaint analysis AI. 
Extract structured information from the complaint below.

Complaint Title: {title}
Complaint Description: {description}

Extract and respond in JSON format with exactly these fields:
{{
  "category": "<one of: electrical, plumbing, hvac, structural, elevator, fire_safety, security, cleaning, it_network, general>",
  "location": "<specific location within building if mentioned>",
  "equipment_type": "<specific equipment mentioned, e.g., AC, elevator, generator, pump>",
  "severity_hints": "<words indicating urgency: smoke, smell, flood, sparks, stuck, etc.>",
  "issue_summary": "<one sentence describing the core issue>",
  "affected_area": "<area or department affected>"
}}

Only respond with the JSON object, no other text."""


class ComplaintUnderstandingAgent(BaseAgent):
    name = "complaint_understanding"
    description = "Extracts location, category, severity from complaint text"

    async def _execute(self, state: dict) -> dict:
        prompt = UNDERSTANDING_PROMPT.format(
            title=state.get("complaint_title", ""),
            description=state.get("complaint_text", ""),
        )

        response = await self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        state["extracted_category"] = parsed.get("category", state.get("category", "general"))
        state["extracted_location"] = parsed.get("location", state.get("location", ""))
        state["extracted_equipment_type"] = parsed.get("equipment_type", "")
        state["extracted_severity_hints"] = parsed.get("severity_hints", "")

        return state

    def _parse_json_response(self, response: str) -> dict:
        try:
            # Find JSON in response
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}

    async def _fallback(self, state: dict) -> dict:
        # Keyword-based fallback classification
        text = (state.get("complaint_text", "") + " " + state.get("complaint_title", "")).lower()
        
        keyword_map = {
            "electrical": ["electric", "wire", "power", "circuit", "switch", "socket", "short", "spark"],
            "plumbing": ["water", "pipe", "leak", "drain", "tap", "flood", "sewage"],
            "hvac": ["ac", "air condition", "hvac", "ventilation", "cooling", "heating", "fan"],
            "elevator": ["lift", "elevator", "stuck"],
            "fire_safety": ["fire", "smoke", "sprinkler", "alarm", "extinguisher"],
            "structural": ["crack", "ceiling", "wall", "floor", "roof", "broken"],
        }

        detected = "general"
        for cat, keywords in keyword_map.items():
            if any(kw in text for kw in keywords):
                detected = cat
                break

        state["extracted_category"] = detected
        return state
