"""
BuildWise AI — Knowledge Agent (RAG-powered)
Retrieves repair procedures from the knowledge base.
"""
from agents.base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):
    name = "knowledge"
    description = "Retrieves repair procedures from RAG knowledge base"

    async def _execute(self, state: dict) -> dict:
        from services.rag_service import search_knowledge_base
        
        query = f"{state.get('extracted_category', '')} {state.get('diagnosis', '')} {state.get('extracted_equipment_type', '')} repair procedure"
        
        results = await search_knowledge_base(query, limit=3)
        
        if results:
            procedures = "\n\n".join([r.get("text", "") for r in results])
            state["repair_procedures"] = procedures
            state["relevant_docs"] = [r.get("source", "") for r in results]
        else:
            state["repair_procedures"] = state.get("suggested_repair", "Follow standard maintenance procedure.")
            state["relevant_docs"] = []

        return state

    async def _fallback(self, state: dict) -> dict:
        state["repair_procedures"] = state.get("suggested_repair", "Follow standard maintenance SOP.")
        state["relevant_docs"] = []
        return state


"""
BuildWise AI — Technician Recommendation Agent
"""
import structlog
logger = structlog.get_logger()


class TechnicianRecommendationAgent(BaseAgent):
    name = "technician_recommendation"
    description = "Recommends best technician based on skill, availability, rating"

    async def _execute(self, state: dict) -> dict:
        from database import AsyncSessionLocal
        from models.technician import Technician
        from sqlalchemy import select

        category = state.get("extracted_category", state.get("category", "general"))
        skill_map = {
            "electrical": "electrical",
            "plumbing": "plumbing",
            "hvac": "hvac",
            "elevator": "electrical",
            "fire_safety": "fire_safety",
            "structural": "civil",
            "cleaning": "cleaning",
            "general": "general",
        }
        required_skill = skill_map.get(category, "general")

        import database
        from models.technician import Technician
        from sqlalchemy import select

        async with database.AsyncSessionLocal() as db:
            result = await db.execute(
                select(Technician).where(
                    Technician.is_available == True
                )
            )
            technicians = result.scalars().all()

        # Filter by skill
        skilled = [t for t in technicians if t.skills and required_skill in t.skills]
        pool = skilled if skilled else technicians

        if not pool:
            logger.warning("No available technicians found", category=category)
            state["recommended_technician_id"] = None
            state["technician_recommendation_reasoning"] = "No available technicians found."
            return state

        # Score technicians based on rating and experience
        def score(t: Technician) -> float:
            rating = t.rating if t.rating else 5.0
            exp = t.experience_years if t.experience_years else 1.0
            return (rating / 5.0) * 0.7 + min(exp / 10.0, 1.0) * 0.3

        best = max(pool, key=score)
        state["recommended_technician_id"] = best.id
        state["technician_recommendation_reasoning"] = (
            f"Selected {best.full_name} — "
            f"Rating: {best.rating}/5, Skills: {', '.join(best.skills or [])}"
        )

        return state

    async def _fallback(self, state: dict) -> dict:
        state["recommended_technician_id"] = None
        state["technician_recommendation_reasoning"] = "Could not recommend technician (service error)."
        return state
