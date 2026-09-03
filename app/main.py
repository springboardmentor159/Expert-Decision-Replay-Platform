from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine

# =========================================================
# IMPORT ALL MODELS
# =========================================================

import app.models


# =========================================================
# IMPORT ROUTERS
# =========================================================

from app.routers.security import router as security_router
from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.decisions import router as decision_router
from app.routers.alternatives import router as alternative_router
from app.routers.comments import router as comment_router
from app.routers.discussion_threads import router as discussion_thread_router
from app.routers.meeting_notes import router as meeting_note_router
from app.routers.scoring import router as scoring_router
from app.routers.expert_evaluations import router as expert_evaluation_router
from app.routers.dashboard import router as dashboard_router
from app.routers.audit import router as audit_router

from app.routers import tags
from app.routers.approvals import router as approval_router
from app.routers.reports import router as reports_router
# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Expert Decision Replay Platform"
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(decision_router)

app.include_router(alternative_router)

app.include_router(comment_router)

app.include_router(discussion_thread_router)

app.include_router(meeting_note_router)

app.include_router(tags.router)

app.include_router(scoring_router)

app.include_router(expert_evaluation_router)

app.include_router(dashboard_router)

app.include_router(audit_router)

app.include_router(approval_router)

app.include_router(security_router)

app.include_router(reports_router)