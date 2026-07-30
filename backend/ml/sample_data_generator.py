"""
BuildWise AI — Sample Data Generator
Generates realistic maintenance dataset for ML training and demos
"""
import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path("datasets")
OUTPUT_DIR.mkdir(exist_ok=True)

BUILDINGS = [
    {"id": "b1", "name": "Engineering Block A", "type": "college"},
    {"id": "b2", "name": "Admin Tower", "type": "office"},
    {"id": "b3", "name": "Central Hospital Wing", "type": "hospital"},
    {"id": "b4", "name": "Shopping Complex G-Block", "type": "mall"},
    {"id": "b5", "name": "Apartment Complex Phase 2", "type": "residential"},
]

CATEGORIES = ["electrical", "plumbing", "hvac", "structural", "elevator", "fire_safety", "cleaning", "general"]
PRIORITIES = ["low", "medium", "high", "critical", "emergency"]
STATUSES = ["submitted", "diagnosed", "assigned", "in_progress", "completed"]
EQUIPMENT_TYPES = ["elevator", "ac", "generator", "pump", "electrical_panel", "hvac", "boiler", "fire_system"]

COMPLAINT_TEMPLATES = [
    ("Water leaking from ceiling in room {room}", "plumbing"),
    ("Electrical short circuit in {floor} floor corridor", "electrical"),
    ("AC unit not cooling properly in {dept}", "hvac"),
    ("Elevator stuck at floor {floor}", "elevator"),
    ("Smoke detector alarm triggered in {dept}", "fire_safety"),
    ("Power failure in {floor} floor", "electrical"),
    ("Broken window in room {room}", "structural"),
    ("Water supply disrupted in {floor}", "plumbing"),
    ("Generator not starting during power cut", "electrical"),
    ("Wall crack noticed in staircase {floor}", "structural"),
]

def gen_complaints(n=200):
    complaints = []
    for i in range(n):
        template, cat = random.choice(COMPLAINT_TEMPLATES)
        title = template.format(room=random.randint(100, 999), floor=random.randint(1, 10), dept=random.choice(["IT", "HR", "Labs", "Cafeteria"]))
        created = datetime.utcnow() - timedelta(days=random.randint(0, 365))
        priority = random.choices(PRIORITIES, weights=[30, 35, 20, 10, 5])[0]
        status = random.choice(STATUSES)
        complaints.append({
            "ticket_number": f"BW-{created.strftime('%Y%m%d')}-{i:04d}",
            "title": title,
            "description": f"Issue reported by resident/employee. {title}. Needs immediate attention.",
            "category": cat,
            "priority": priority,
            "status": status,
            "building": random.choice(BUILDINGS)["name"],
            "estimated_labor_cost": round(random.uniform(500, 5000), 2),
            "estimated_material_cost": round(random.uniform(200, 3000), 2),
            "actual_cost": round(random.uniform(700, 7000), 2),
            "resolution_hours": round(random.uniform(0.5, 48), 1),
            "resolution_rating": random.randint(3, 5),
            "created_at": created.isoformat(),
        })
    return complaints

def gen_equipment(n=50):
    equipment = []
    for i in range(n):
        eq_type = random.choice(EQUIPMENT_TYPES)
        install_date = datetime.utcnow() - timedelta(days=random.randint(180, 3650))
        last_maint = install_date + timedelta(days=random.randint(30, 300))
        age_days = (datetime.utcnow() - install_date).days
        health = max(10.0, min(100.0, 100 - age_days * 0.02 - random.uniform(0, 20)))
        failure_prob = max(0.01, min(0.99, 1 - health / 100 + random.uniform(-0.1, 0.1)))
        equipment.append({
            "id": f"eq{i:03d}",
            "name": f"{eq_type.replace('_', ' ').title()} Unit {i+1}",
            "equipment_type": eq_type,
            "building": random.choice(BUILDINGS)["name"],
            "installation_date": install_date.isoformat(),
            "last_maintenance_date": last_maint.isoformat(),
            "age_days": age_days,
            "health_score": round(health, 2),
            "failure_probability": round(failure_prob, 3),
            "maintenance_count": random.randint(0, 15),
            "total_cost": round(random.uniform(0, 50000), 2),
            "is_critical": random.choice([True, False]),
            "status": random.choice(["operational", "operational", "operational", "degraded", "maintenance"]),
        })
    return equipment

def gen_maintenance_history(n=300):
    records = []
    for i in range(n):
        performed = datetime.utcnow() - timedelta(days=random.randint(0, 730))
        health_before = random.uniform(40, 80)
        health_after = min(100, health_before + random.uniform(10, 30))
        records.append({
            "id": f"mh{i:04d}",
            "equipment_id": f"eq{random.randint(0, 49):03d}",
            "maintenance_type": random.choice(["preventive", "corrective", "emergency"]),
            "description": random.choice(["Oil change and lubrication", "Component replacement", "System reset and calibration", "Full inspection", "Emergency repair"]),
            "duration_hours": round(random.uniform(0.5, 8), 1),
            "labor_cost": round(random.uniform(500, 3000), 2),
            "material_cost": round(random.uniform(200, 2000), 2),
            "total_cost": round(random.uniform(700, 5000), 2),
            "health_score_before": round(health_before, 2),
            "health_score_after": round(health_after, 2),
            "technician": f"TECH{random.randint(1, 15):03d}",
            "performed_at": performed.isoformat(),
        })
    return records

def gen_technicians(n=15):
    skills_pool = ["electrical", "plumbing", "hvac", "civil", "fire_safety", "it_network", "elevator", "general"]
    names = ["Rajesh Kumar", "Priya Sharma", "Arjun Singh", "Meena Patel", "Vikram Nair",
             "Sunita Reddy", "Karthik Iyer", "Anita Joshi", "Suresh Verma", "Deepa Rao",
             "Manoj Gupta", "Lakshmi Pillai", "Rohan Das", "Kavitha Menon", "Ajay Shetty"]
    technicians = []
    for i, name in enumerate(names[:n]):
        technicians.append({
            "id": f"tech{i+1:03d}",
            "employee_id": f"EMP{i+1:04d}",
            "full_name": name,
            "email": f"{name.lower().replace(' ', '.')}@buildwise.ai",
            "phone": f"+91 {random.randint(7000000000, 9999999999)}",
            "skills": random.sample(skills_pool, random.randint(1, 3)),
            "experience_years": random.randint(1, 20),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "total_jobs": random.randint(50, 500),
            "completed_jobs": random.randint(48, 490),
            "performance_score": round(random.uniform(70, 100), 1),
            "status": random.choices(["available", "busy", "off_duty"], weights=[60, 30, 10])[0],
            "shift_start": "09:00",
            "shift_end": "18:00",
        })
    return technicians

if __name__ == "__main__":
    # Generate JSON files
    complaints = gen_complaints(200)
    equipment = gen_equipment(50)
    history = gen_maintenance_history(300)
    technicians = gen_technicians(15)

    (OUTPUT_DIR / "sample_complaints.json").write_text(json.dumps(complaints, indent=2))
    (OUTPUT_DIR / "sample_equipment.json").write_text(json.dumps(equipment, indent=2))
    (OUTPUT_DIR / "sample_technicians.json").write_text(json.dumps(technicians, indent=2))

    # CSV for ML training
    with open(OUTPUT_DIR / "sample_maintenance_history.csv", "w", newline="") as f:
        if history:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)

    # Equipment CSV for ML
    with open(OUTPUT_DIR / "equipment_features.csv", "w", newline="") as f:
        if equipment:
            writer = csv.DictWriter(f, fieldnames=equipment[0].keys())
            writer.writeheader()
            writer.writerows(equipment)

    print(f"[OK] Generated:")
    print(f"   {len(complaints)} complaint records -> sample_complaints.json")
    print(f"   {len(equipment)} equipment records -> sample_equipment.json")
    print(f"   {len(history)} maintenance records -> sample_maintenance_history.csv")
    print(f"   {len(technicians)} technician records -> sample_technicians.json")
    print(f"   Equipment ML features -> equipment_features.csv")
