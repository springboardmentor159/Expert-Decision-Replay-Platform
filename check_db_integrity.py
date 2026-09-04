from sqlalchemy import text

from app.db.database import engine

checks = {
    "documents": "select count(*) from decision_documents",
    "orphan_documents": "select count(*) from decision_documents d left join decisions x on x.id=d.decision_id where x.id is null",
    "orphan_decisions": "select count(*) from decisions d left join users u on u.id=d.created_by where u.id is null",
}

with engine.connect() as connection:
    print({name: connection.execute(text(sql)).scalar() for name, sql in checks.items()})
