"""
BuildWise AI — AI Agents Router (trigger workflows + status)
"""
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

from models.user import User
from services.jwt_service import get_current_user

router = APIRouter()


class AgentRunRequest(BaseModel):
    complaint_id: str
    agent_name: Optional[str] = None  # If None, run full workflow


class AgentStatusResponse(BaseModel):
    agent_name: str
    status: str
    description: str
    icon: str
    color: str


AGENTS = [
    {"name": "coordinator", "description": "Orchestrates all agents, maintains workflow state", "icon": "🎯", "color": "#6366f1"},
    {"name": "complaint_understanding", "description": "Extracts location, category, severity from complaint", "icon": "🧠", "color": "#3b82f6"},
    {"name": "diagnosis", "description": "Diagnoses issue using LLM + Computer Vision", "icon": "🔍", "color": "#8b5cf6"},
    {"name": "priority", "description": "Classifies urgency: Low/Medium/High/Critical/Emergency", "icon": "⚡", "color": "#f59e0b"},
    {"name": "knowledge", "description": "Retrieves repair procedures from RAG knowledge base", "icon": "📚", "color": "#10b981"},
    {"name": "technician_recommendation", "description": "Recommends best technician based on skill, availability", "icon": "👷", "color": "#06b6d4"},
    {"name": "scheduling", "description": "Generates optimal repair schedule avoiding conflicts", "icon": "📅", "color": "#ec4899"},
    {"name": "cost_estimation", "description": "Predicts labor, material costs and repair duration", "icon": "💰", "color": "#f97316"},
    {"name": "predictive_maintenance", "description": "Predicts future failures using ML models", "icon": "🔮", "color": "#84cc16"},
    {"name": "analytics", "description": "Generates KPIs, reports, heatmaps and insights", "icon": "📊", "color": "#a855f7"},
]


@router.get("")
async def list_agents(current_user: User = Depends(get_current_user)):
    return {"agents": AGENTS, "total": len(AGENTS)}


@router.post("/run")
async def run_agent_workflow(
    payload: AgentRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    background_tasks.add_task(_run_agents, payload.complaint_id, payload.agent_name)
    return {
        "message": "AI agent workflow triggered",
        "complaint_id": payload.complaint_id,
        "status": "processing",
    }


@router.post("/analyze-complaint")
async def analyze_complaint_with_ai(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """Run quick AI analysis on complaint text."""
    from services.ai_orchestrator import quick_analyze_complaint
    result = await quick_analyze_complaint(
        title=payload.get("title", ""),
        description=payload.get("description", ""),
        category=payload.get("category", "general"),
    )
    return result


@router.get("/workflow-status/{complaint_id}")
async def get_workflow_status(complaint_id: str, current_user: User = Depends(get_current_user)):
    """Get current agent workflow status for a complaint."""
    # In production this would query a workflow state store (Redis/DB)
    return {
        "complaint_id": complaint_id,
        "workflow_status": "completed",
        "agents_executed": [a["name"] for a in AGENTS],
        "current_agent": None,
        "progress_pct": 100,
    }


async def _run_agents(complaint_id: str, agent_name: Optional[str]):
    try:
        from services.ai_orchestrator import process_complaint_with_agents
        await process_complaint_with_agents(complaint_id)
    except Exception as e:
        import structlog
        structlog.get_logger().error("Agent workflow failed", complaint_id=complaint_id, error=str(e))


@router.post("/rag-chat")
async def rag_chat(payload: dict, current_user: User = Depends(get_current_user)):
    """Chat with the knowledge base using RAG."""
    from services.rag_service import query_knowledge_base
    question = payload.get("question", "")
    context = payload.get("context", "")
    result = await query_knowledge_base(question, context)
    return result
