"""
BuildWise AI — Diagnosis Agent
Predicts probable issue, suggests repair, parts, and estimates duration.
"""
import json
import re
from agents.base_agent import BaseAgent


DIAGNOSIS_PROMPT = """You are an expert building maintenance engineer AI.

Complaint: {complaint}
Category: {category}
Equipment Type: {equipment_type}
Location: {location}

Based on this, provide a technical diagnosis. Respond in JSON:
{{
  "diagnosis": "<technical diagnosis of probable issue>",
  "root_cause": "<likely root cause>",
  "suggested_repair": "<step-by-step repair procedure>",
  "suggested_parts": ["<part1>", "<part2>"],
  "estimated_duration_hours": <number>,
  "skill_required": "<skill needed: electrician, plumber, hvac_technician, etc.>",
  "safety_precautions": ["<precaution1>", "<precaution2>"],
  "urgency_indicator": "<immediate|within_24h|within_week|scheduled>"
}}

Only respond with JSON."""


class DiagnosisAgent(BaseAgent):
    name = "diagnosis"
    description = "Diagnoses issue using LLM, suggests repair and spare parts"

    async def _execute(self, state: dict) -> dict:
        prompt = DIAGNOSIS_PROMPT.format(
            complaint=f"{state.get('complaint_title', '')} — {state.get('complaint_text', '')}",
            category=state.get("extracted_category", state.get("category", "general")),
            equipment_type=state.get("extracted_equipment_type", "unknown"),
            location=state.get("extracted_location", "unspecified"),
        )

        response = await self._call_llm(prompt)
        parsed = self._parse_json(response)

        state["diagnosis"] = parsed.get("diagnosis", "Issue under investigation")
        state["suggested_repair"] = parsed.get("suggested_repair", "Standard maintenance procedure")
        state["suggested_parts"] = parsed.get("suggested_parts", [])
        state["estimated_duration_hours"] = float(parsed.get("estimated_duration_hours", 2.0))

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
        category = state.get("extracted_category", "general")
        defaults = {
            "electrical": {
                "diagnosis": "Electrical fault detected. Possible wiring issue or overload.",
                "suggested_repair": "1. Switch off main breaker. 2. Inspect wiring. 3. Replace faulty components.",
                "suggested_parts": ["Circuit breaker", "Electrical tape", "Wire connector"],
                "estimated_duration_hours": 3.0,
            },
            "plumbing": {
                "diagnosis": "Plumbing issue detected. Possible pipe blockage or leakage.",
                "suggested_repair": "1. Shut off water supply. 2. Inspect pipes. 3. Replace damaged sections.",
                "suggested_parts": ["PVC pipe", "Plumber tape", "Pipe wrench"],
                "estimated_duration_hours": 2.0,
            },
            "hvac": {
                "diagnosis": "HVAC system malfunction. Possible refrigerant leak or filter clogging.",
                "suggested_repair": "1. Check refrigerant levels. 2. Clean/replace filters. 3. Inspect compressor.",
                "suggested_parts": ["Air filter", "Refrigerant", "Compressor belt"],
                "estimated_duration_hours": 4.0,
            },
        }
        d = defaults.get(category, {
            "diagnosis": "General maintenance issue requiring inspection.",
            "suggested_repair": "Perform visual inspection and report findings.",
            "suggested_parts": [],
            "estimated_duration_hours": 1.5,
        })
        state.update(d)
        return state
