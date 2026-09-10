"""
Seed script to ensure standard demo accounts exist for all 4 roles in the database:
- employee@example.com / Password123! (Employee)
- reviewer@example.com / Password123! (Reviewer)
- manager@example.com / Password123! (Manager)
- admin@example.com / Password123! (Administrator)
"""
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

DEMO_USERS = [
    {
        "full_name": "Alice Employee",
        "email": "employee@example.com",
        "password": "Password123!",
        "role": "Employee",
        "department": "Engineering",
        "designation": "Software Engineer",
        "employee_id": "EMP-1001",
        "phone_number": "123-456-7890"
    },
    {
        "full_name": "Bob Reviewer",
        "email": "reviewer@example.com",
        "password": "Password123!",
        "role": "Reviewer",
        "department": "Engineering",
        "designation": "Principal Engineer",
        "employee_id": "REV-2001",
        "phone_number": "123-456-7891"
    },
    {
        "full_name": "Charlie Manager",
        "email": "manager@example.com",
        "password": "Password123!",
        "role": "Manager",
        "department": "Engineering",
        "designation": "Engineering Manager",
        "employee_id": "MGR-3001",
        "phone_number": "123-456-7892"
    },
    {
        "full_name": "Diana Administrator",
        "email": "admin@example.com",
        "password": "Password123!",
        "role": "Administrator",
        "department": "Executive",
        "designation": "System Administrator",
        "employee_id": "ADM-4001",
        "phone_number": "123-456-7893"
    },
]

def seed():
    db = SessionLocal()
    try:
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                new_user = User(
                    full_name=u["full_name"],
                    email=u["email"],
                    role=u["role"],
                    hashed_password=hash_password(u["password"]),
                    department=u["department"],
                    designation=u["designation"],
                    employee_id=u["employee_id"],
                    phone_number=u["phone_number"]
                )
                db.add(new_user)
                print(f"Created user: {u['email']} ({u['role']})")
            else:
                # Update role and password if needed
                existing.role = u["role"]
                existing.hashed_password = hash_password(u["password"])
                existing.department = u["department"]
                print(f"User exists, updated: {u['email']} ({u['role']})")
        db.commit()
        print("Demo users seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
