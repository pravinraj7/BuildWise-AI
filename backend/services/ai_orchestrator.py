"""
BuildWise AI — AI Orchestrator Service
The main orchestrator that coordinates all 10 AI agents using LangGraph.
"""
import asyncio
from typing import TypedDict, Optional, Annotated
from datetime import datetime
import structlog

logger = structlog.get_logger()

# ── Agent Imports ─────────────────────────────────────────────────────────────
from agents.complaint_understanding_agent import ComplaintUnderstandingAgent
from agents.diagnosis_agent import DiagnosisAgent
from agents.priority_agent import PriorityAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.technician_recommendation_agent import TechnicianRecommendationAgent
from agents.scheduling_agent import SchedulingAgent
from agents.cost_estimation_agent import CostEstimationAgent
from agents.analytics_agent import AnalyticsAgent


# ── Workflow State ─────────────────────────────────────────────────────────────
class WorkflowState(TypedDict):
    complaint_id: str
    complaint_text: str
    complaint_title: str
    category: Optional[str]
    building_id: Optional[str]
    floor_id: Optional[str]
    department: Optional[str]
    location: Optional[str]

    # Understanding Agent output
    extracted_category: Optional[str]
    extracted_location: Optional[str]
    extracted_severity_hints: Optional[str]
    extracted_equipment_type: Optional[str]

    # Diagnosis Agent output
    diagnosis: Optional[str]
    suggested_repair: Optional[str]
    suggested_parts: Optional[list]
    estimated_duration_hours: Optional[float]

    # Priority Agent output
    priority: Optional[str]
    is_emergency: Optional[bool]
    requires_evacuation: Optional[bool]
    priority_reasoning: Optional[str]

    # Knowledge Agent output
    repair_procedures: Optional[str]
    relevant_docs: Optional[list]

    # Technician Recommendation
    recommended_technician_id: Optional[str]
    technician_recommendation_reasoning: Optional[str]

    # Scheduling Agent
    scheduled_start: Optional[str]
    scheduled_end: Optional[str]

    # Cost Estimation
    estimated_labor_cost: Optional[float]
    estimated_material_cost: Optional[float]
    estimated_total_cost: Optional[float]

    # Errors & Status
    errors: list
    completed_agents: list
    workflow_status: str


async def process_complaint_with_agents(complaint_id: str) -> dict:
    """
    Main entry point: runs the full 10-agent LangGraph workflow for a complaint.
    """
    logger.info("Starting AI agent workflow", complaint_id=complaint_id)

    # Fetch complaint from DB
    import database
    from models.complaint import Complaint, ComplaintStatus, ComplaintTimeline
    from sqlalchemy import select

    async with database.AsyncSessionLocal() as db:
        result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
        complaint = result.scalar_one_or_none()
        if not complaint:
            logger.error("Complaint not found for AI processing", complaint_id=complaint_id)
            return {}

        # Update status to AI_PROCESSING
        complaint.status = ComplaintStatus.AI_PROCESSING
        timeline = ComplaintTimeline(
            complaint_id=complaint_id,
            action="AI_PROCESSING_STARTED",
            description="AI agents are analyzing your complaint…",
            actor_type="agent",
            actor_name="Coordinator Agent",
        )
        db.add(timeline)
        await db.commit()

        # Initialize workflow state
        state = WorkflowState(
            complaint_id=complaint_id,
            complaint_text=complaint.description,
            complaint_title=complaint.title,
            category=complaint.category.value if complaint.category else "general",
            building_id=complaint.building_id,
            floor_id=complaint.floor_id,
            department=None,
            location=complaint.location_description,
            errors=[],
            completed_agents=[],
            workflow_status="running",
            extracted_category=None, extracted_location=None,
            extracted_severity_hints=None, extracted_equipment_type=None,
            diagnosis=None, suggested_repair=None, suggested_parts=None, estimated_duration_hours=None,
            priority=None, is_emergency=None, requires_evacuation=None, priority_reasoning=None,
            repair_procedures=None, relevant_docs=None,
            recommended_technician_id=None, technician_recommendation_reasoning=None,
            scheduled_start=None, scheduled_end=None,
            estimated_labor_cost=None, estimated_material_cost=None, estimated_total_cost=None,
        )

    # ── Run Agents Sequentially ───────────────────────────────────────────────
    agents_pipeline = [
        ("complaint_understanding", ComplaintUnderstandingAgent()),
        ("diagnosis", DiagnosisAgent()),
        ("priority", PriorityAgent()),
        ("knowledge", KnowledgeAgent()),
        ("technician_recommendation", TechnicianRecommendationAgent()),
        ("scheduling", SchedulingAgent()),
        ("cost_estimation", CostEstimationAgent()),
        ("analytics", AnalyticsAgent()),
    ]

    for agent_name, agent in agents_pipeline:
        try:
            logger.info(f"Running agent: {agent_name}", complaint_id=complaint_id)
            state = await agent.run(state)
            state["completed_agents"].append(agent_name)
        except Exception as e:
            logger.error(f"Agent {agent_name} failed", error=str(e), complaint_id=complaint_id)
            state["errors"].append(f"{agent_name}: {str(e)}")

    # ── Persist Results to DB ─────────────────────────────────────────────────
    async with database.AsyncSessionLocal() as db:
        result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
        complaint = result.scalar_one_or_none()
        if complaint:
            complaint.ai_diagnosis = state.get("diagnosis")
            complaint.ai_suggested_repair = state.get("suggested_repair")
            complaint.ai_suggested_parts = state.get("suggested_parts")
            complaint.ai_processed_at = datetime.utcnow()
            complaint.estimated_labor_cost = state.get("estimated_labor_cost")
            complaint.estimated_material_cost = state.get("estimated_material_cost")
            complaint.estimated_total_cost = state.get("estimated_total_cost")
            complaint.estimated_duration_hours = state.get("estimated_duration_hours")
            complaint.status = ComplaintStatus.DIAGNOSED

            if state.get("priority"):
                from models.complaint import PriorityLevel
                try:
                    complaint.priority = PriorityLevel(state["priority"])
                except ValueError:
                    pass

            complaint.is_emergency = state.get("is_emergency", False)
            complaint.requires_evacuation = state.get("requires_evacuation", False)

            if state.get("recommended_technician_id"):
                complaint.assigned_technician_id = state["recommended_technician_id"]
                complaint.status = ComplaintStatus.ASSIGNED
                complaint.assigned_at = datetime.utcnow()

            # Add completion timeline
            timeline = ComplaintTimeline(
                complaint_id=complaint_id,
                action="AI_ANALYSIS_COMPLETE",
                description=f"AI analysis completed. Priority: {state.get('priority', 'medium')}. {len(state['completed_agents'])} agents executed.",
                actor_type="agent",
                actor_name="Coordinator Agent",
            )
            db.add(timeline)
            await db.commit()

    state["workflow_status"] = "completed"
    logger.info("AI workflow completed", complaint_id=complaint_id, agents=len(state["completed_agents"]))
    return dict(state)


async def quick_analyze_complaint(title: str, description: str, category: str) -> dict:
    """Quick analysis without full workflow — for real-time feedback."""
    agent = PriorityAgent()
    state = WorkflowState(
        complaint_id="quick", complaint_text=description, complaint_title=title,
        category=category, building_id=None, floor_id=None, department=None, location=None,
        errors=[], completed_agents=[], workflow_status="running",
        extracted_category=None, extracted_location=None,
        extracted_severity_hints=None, extracted_equipment_type=None,
        diagnosis=None, suggested_repair=None, suggested_parts=None, estimated_duration_hours=None,
        priority=None, is_emergency=None, requires_evacuation=None, priority_reasoning=None,
        repair_procedures=None, relevant_docs=None,
        recommended_technician_id=None, technician_recommendation_reasoning=None,
        scheduled_start=None, scheduled_end=None,
        estimated_labor_cost=None, estimated_material_cost=None, estimated_total_cost=None,
    )

    understanding_agent = ComplaintUnderstandingAgent()
    state = await understanding_agent.run(state)
    state = await agent.run(state)

    return {
        "priority": state.get("priority", "medium"),
        "is_emergency": state.get("is_emergency", False),
        "extracted_category": state.get("extracted_category", category),
        "priority_reasoning": state.get("priority_reasoning", ""),
    }
