from app.db.database import Base

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative