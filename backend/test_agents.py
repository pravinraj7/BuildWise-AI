import asyncio
import json
import database
from database import init_db
from services.ai_orchestrator import process_complaint_with_agents, quick_analyze_complaint
from models.complaint import Complaint, PriorityLevel, ComplaintCategory

async def test():
    await init_db()
    res = await quick_analyze_complaint("Elevator Stuck", "Elevator stopped on 3rd floor with people inside", "elevator")
    print("QUICK_ANALYZE_RESULT:")
    print(json.dumps(res, indent=2))
    
    async with database.AsyncSessionLocal() as db:
        c = Complaint(
            ticket_number="TK-TEST-001",
            requester_id="00000000-0000-0000-0000-000000000001",
            building_id="00000000-0000-0000-0000-000000000001",
            title="Pipe Burst in Basement",
            description="Severe water leak in basement pipe, flooding nearby electrical equipment and elevator shaft",
            location_description="Basement B2",
            category=ComplaintCategory.PLUMBING,
            priority=PriorityLevel.HIGH
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        cid = c.id
        
    print(f"Created sample complaint with ID: {cid}")
    state = await process_complaint_with_agents(cid)
    print("FULL_WORKFLOW_RESULT:")
    print(json.dumps({
        "completed_agents": state.get("completed_agents"),
        "priority": state.get("priority"),
        "is_emergency": state.get("is_emergency"),
        "extracted_category": state.get("extracted_category"),
        "diagnosis": state.get("diagnosis"),
        "suggested_repair": state.get("suggested_repair"),
        "estimated_total_cost": state.get("estimated_total_cost"),
        "errors": state.get("errors")
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
