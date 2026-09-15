from sqlalchemy import text
from app.db.database import engine
from app.db.base import Base
import app.models  # load all models


def run_migration():
    print("Creating all new tables if they do not exist...")
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        print("Migrating decisions columns...")
        conn.execute(text("ALTER TABLE decisions ADD COLUMN IF NOT EXISTS evaluation_criteria TEXT;"))
        conn.execute(text("ALTER TABLE decisions ADD COLUMN IF NOT EXISTS final_outcomes TEXT;"))

        # Create enum if not exists
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'implementation_status') THEN
                    CREATE TYPE implementation_status AS ENUM ('Not Started', 'In Progress', 'Completed', 'Blocked', 'Cancelled');
                END IF;
            END $$;
        """))

        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='decisions' AND column_name='implementation_status'
                ) THEN
                    ALTER TABLE decisions ADD COLUMN implementation_status implementation_status DEFAULT 'Not Started' NOT NULL;
                END IF;
            END $$;
        """))

        print("Migrating approvals columns...")
        conn.execute(text("ALTER TABLE approvals ADD COLUMN IF NOT EXISTS sequence_order INTEGER DEFAULT 1 NOT NULL;"))
        conn.execute(text("ALTER TABLE approvals ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;"))
        conn.execute(text("ALTER TABLE approvals ADD COLUMN IF NOT EXISTS is_escalated INTEGER DEFAULT 0 NOT NULL;"))
        conn.execute(text("ALTER TABLE approvals ADD COLUMN IF NOT EXISTS escalated_to_id INTEGER REFERENCES users(id);"))

        conn.commit()
    print("Database migration completed successfully!")


if __name__ == "__main__":
    run_migration()
