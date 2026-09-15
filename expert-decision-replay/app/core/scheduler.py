from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.approval import Approval


scheduler = BackgroundScheduler()


def escalate_overdue_approvals():
    db: Session = SessionLocal()

    try:
        now = datetime.now()

        overdue_approvals = (
            db.query(Approval)
            .filter(
                Approval.status == "Pending",
                Approval.due_at < now,
                Approval.escalated == False
            )
            .all()
        )

        for approval in overdue_approvals:
            approval.escalated = True
            approval.escalated_at = now
            approval.escalation_reason = "Approval deadline exceeded"

        if overdue_approvals:
            db.commit()
            print(
                f"Automatically escalated "
                f"{len(overdue_approvals)} approval(s)"
            )
        else:
            print("No overdue approvals found")

    except Exception as error:
        db.rollback()
        print(f"Scheduler error: {error}")

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        escalate_overdue_approvals,
        "interval",
        minutes=1,
        id="approval_escalation_job",
        replace_existing=True
    )

    scheduler.start()
    print("Automatic escalation scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Automatic escalation scheduler stopped")