"""
BuildWise AI — Scheduling Agent
Generates optimal repair schedule avoiding conflicts.
"""
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
import structlog

logger = structlog.get_logger()


class SchedulingAgent(BaseAgent):
    name = "scheduling"
    description = "Generates optimal repair schedule avoiding conflicts"

    async def _execute(self, state: dict) -> dict:
        if not state.get("recommended_technician_id"):
            state["scheduled_start"] = None
            state["scheduled_end"] = None
            return state

        technician_id = state["recommended_technician_id"]
        duration_hours = state.get("estimated_duration_hours", 2.0)
        priority = state.get("priority", "medium")

        # Get technician's existing schedule
        import database
        from models.schedule import ScheduleSlot
        from sqlalchemy import select

        async with database.AsyncSessionLocal() as db:
            result = await db.execute(
                select(ScheduleSlot).where(
                    ScheduleSlot.technician_id == technician_id,
                ).order_by(ScheduleSlot.end_time.desc())
            )
            existing_schedules = result.scalars().all()

        # Determine start time based on priority
        now = datetime.utcnow()
        if priority == "emergency":
            start_time = now + timedelta(minutes=15)
        elif priority == "critical":
            start_time = now + timedelta(hours=1)
        elif priority == "high":
            start_time = now + timedelta(hours=4)
        elif priority == "medium":
            start_time = self._next_available_slot(now, existing_schedules, timedelta(hours=24))
        else:
            start_time = self._next_available_slot(now, existing_schedules, timedelta(hours=48))

        end_time = start_time + timedelta(hours=duration_hours)

        state["scheduled_start"] = start_time.isoformat()
        state["scheduled_end"] = end_time.isoformat()

        logger.info("Schedule generated", start=start_time.isoformat(), technician=technician_id)
        return state

    def _next_available_slot(self, now: datetime, existing_schedules, preferred_offset: timedelta) -> datetime:
        candidate = now + preferred_offset
        for schedule in existing_schedules:
            if schedule.start_time <= candidate <= schedule.end_time:
                candidate = schedule.end_time + timedelta(minutes=30)
        return candidate

    async def _fallback(self, state: dict) -> dict:
        state["scheduled_start"] = None
        state["scheduled_end"] = None
        return state


"""
BuildWise AI — Cost Estimation Agent
"""

class CostEstimationAgent(BaseAgent):
    name = "cost_estimation"
    description = "Predicts labor, material costs and repair duration"

    LABOR_RATES = {
        "electrical": 800,  # INR per hour
        "plumbing": 600,
        "hvac": 900,
        "elevator": 1200,
        "fire_safety": 1000,
        "structural": 1100,
        "civil": 1000,
        "cleaning": 400,
        "general": 500,
    }

    MATERIAL_ESTIMATES = {
        "electrical": 2500,
        "plumbing": 1800,
        "hvac": 4500,
        "elevator": 8000,
        "fire_safety": 3500,
        "structural": 5000,
        "cleaning": 500,
        "general": 1000,
    }

    async def _execute(self, state: dict) -> dict:
        category = state.get("extracted_category", state.get("category", "general"))
        duration = state.get("estimated_duration_hours", 2.0)
        priority = state.get("priority", "medium")

        labor_rate = self.LABOR_RATES.get(category, 500)
        material_base = self.MATERIAL_ESTIMATES.get(category, 1000)

        # Priority multiplier
        priority_multiplier = {
            "emergency": 2.0, "critical": 1.5, "high": 1.2, "medium": 1.0, "low": 0.9
        }.get(priority, 1.0)

        labor_cost = labor_rate * duration * priority_multiplier
        material_cost = material_base * priority_multiplier
        total_cost = labor_cost + material_cost

        state["estimated_labor_cost"] = round(labor_cost, 2)
        state["estimated_material_cost"] = round(material_cost, 2)
        state["estimated_total_cost"] = round(total_cost, 2)

        return state

    async def _fallback(self, state: dict) -> dict:
        state["estimated_labor_cost"] = 1500.0
        state["estimated_material_cost"] = 2000.0
        state["estimated_total_cost"] = 3500.0
        return state


"""
BuildWise AI — Analytics Agent
"""

class AnalyticsAgent(BaseAgent):
    name = "analytics"
    description = "Updates building health score and analytics"

    async def _execute(self, state: dict) -> dict:
        # Update building health score based on complaint count and priority
        building_id = state.get("building_id")
        if not building_id:
            return state

        priority = state.get("priority", "medium")
        health_deduction = {
            "emergency": 5.0, "critical": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5
        }.get(priority, 1.0)

        import database
        from models.building import Building
        from sqlalchemy import select

        async with database.AsyncSessionLocal() as db:
            result = await db.execute(select(Building).where(Building.id == building_id))
            building = result.scalar_one_or_none()
            if building and hasattr(building, "health_score"):
                building.health_score = max(0.0, building.health_score - health_deduction)
                await db.commit()

        return state

    async def _fallback(self, state: dict) -> dict:
        return state
