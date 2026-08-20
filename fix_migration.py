"""
Fix the alembic migration history
"""
from app.db.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Get current version
    result = db.execute(text("SELECT * FROM alembic_version"))
    rows = result.fetchall()
    print("Current migration versions:", rows)
    
    # Delete the invalid version
    db.execute(text("DELETE FROM alembic_version WHERE version_num = 'e767bdd1c23e'"))
    db.commit()
    print("Deleted invalid migration version")
    
    # Check again
    result = db.execute(text("SELECT * FROM alembic_version"))
    rows = result.fetchall()
    print("Updated migration versions:", rows)
    
finally:
    db.close()
