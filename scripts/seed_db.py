import os
import shutil
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.db.database import SessionLocal, engine
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.team import Team, user_teams
from app.models.tag import Tag, decision_tags
from app.models.decision import Decision, DecisionStatus, ImplementationStatus
from app.models.alternative import Alternative, RiskLevel
from app.models.approval import Approval, ApprovalStatus
from app.models.comment import Comment
from app.models.notification import Notification, NotificationType
from app.models.audit import AuditLog, AuditAction, DecisionVersion, SecurityLog
from app.services.security import hash_password

def clean_and_seed():
    print("=" * 60)
    print("STARTING COMPLETE DATABASE CLEANUP & RE-SEEDING")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Truncate all tables in database
        print("[1/5] Truncating all tables with CASCADE...")
        truncate_sql = text("""
            TRUNCATE TABLE 
                decision_attachments,
                notifications,
                user_teams,
                teams,
                decision_tags,
                tags,
                meeting_notes,
                comments,
                discussion_threads,
                approvals,
                decision_versions,
                audit_logs,
                security_logs,
                access_logs,
                alternatives,
                decisions,
                users,
                organizations
            RESTART IDENTITY CASCADE;
        """)
        db.execute(truncate_sql)
        db.commit()
        print(" -> All database tables truncated and sequences reset to 1.")

        # 2. Clean uploads directory
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if os.path.exists(uploads_dir):
            for item in os.listdir(uploads_dir):
                item_path = os.path.join(uploads_dir, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    print(f"Warning cleaning {item_path}: {e}")
            print(f" -> Cleaned uploads directory: {uploads_dir}")

        # 3. Create Organizations
        print("[2/5] Creating Organizations...")
        org1 = Organization(
            name="Sprint Verification Org",
            description="Enterprise Software Architecture & Strategic Decision Governance Organization"
        )
        org2 = Organization(
            name="Apex Health Innovations",
            description="Clinical & Health Systems Engineering Division"
        )
        db.add_all([org1, org2])
        db.flush()
        print(f" -> Created {org1.name} (ID: {org1.id}) and {org2.name} (ID: {org2.id})")

        # 4. Create Users (all with password: password123)
        print("[3/5] Creating Users with standard credentials ('password123')...")
        hashed_pwd = hash_password("password123")

        admin_user = User(
            full_name="John Doe",
            email="admin@example.com",
            role=UserRole.ADMINISTRATOR,
            password=hashed_pwd,
            employee_id="EMP-ADM01",
            department="Executive Operations",
            designation="Chief Information Officer",
            phone_number="+1-555-0100",
            organization_id=org1.id
        )

        manager_user = User(
            full_name="Sarah Jenkins",
            email="manager@example.com",
            role=UserRole.MANAGER,
            password=hashed_pwd,
            employee_id="EMP-MGR01",
            department="Engineering Directorate",
            designation="VP of Engineering & Architecture",
            phone_number="+1-555-0101",
            organization_id=org1.id
        )

        reviewer_user = User(
            full_name="Raftaar Singh",
            email="reviewer@example.com",
            role=UserRole.REVIEWER,
            password=hashed_pwd,
            employee_id="EMP-REV01",
            department="Operations",
            designation="Principal Enterprise Architect",
            phone_number="+1-555-0102",
            organization_id=org1.id
        )

        sec_reviewer = User(
            full_name="Elena Vance",
            email="sec_reviewer@example.com",
            role=UserRole.REVIEWER,
            password=hashed_pwd,
            employee_id="EMP-REV02",
            department="Information Security",
            designation="Chief Security Architect",
            phone_number="+1-555-0103",
            organization_id=org1.id
        )

        employee_user = User(
            full_name="Alex Chen",
            email="employee@example.com",
            role=UserRole.EMPLOYEE,
            password=hashed_pwd,
            employee_id="EMP-DEV01",
            department="Platform Engineering",
            designation="Senior Distributed Systems Engineer",
            phone_number="+1-555-0104",
            organization_id=org1.id
        )

        sujal_user = User(
            full_name="Sujal Sharma",
            email="sujal@example.com",
            role=UserRole.EMPLOYEE,
            password=hashed_pwd,
            employee_id="EMP-DEV02",
            department="Core Infrastructure",
            designation="Fullstack Lead Engineer",
            phone_number="+1-555-0105",
            organization_id=org1.id
        )

        users_list = [admin_user, manager_user, reviewer_user, sec_reviewer, employee_user, sujal_user]
        db.add_all(users_list)
        db.flush()
        print(f" -> Created {len(users_list)} users with email logins.")

        # 5. Create Teams
        print("[4/5] Creating Teams & Rosters...")
        team_arch = Team(
            name="Core Infrastructure & Architecture",
            description="Designs resilient cloud infrastructure and system architecture standards.",
            lead_id=manager_user.id,
            organization_id=org1.id
        )
        team_sec = Team(
            name="Security & Compliance Governance",
            description="Ensures zero-trust compliance, cryptographic standards, and access control.",
            lead_id=sec_reviewer.id,
            organization_id=org1.id
        )
        team_fe = Team(
            name="Frontend Platform Team",
            description="Maintains UI design systems, client state standards, and web performance.",
            lead_id=sujal_user.id,
            organization_id=org1.id
        )
        db.add_all([team_arch, team_sec, team_fe])
        db.flush()

        # Add memberships
        team_arch.members.extend([employee_user, sujal_user, reviewer_user, manager_user])
        team_sec.members.extend([sec_reviewer, reviewer_user, employee_user])
        team_fe.members.extend([sujal_user, employee_user])
        db.flush()
        print(" -> Created 3 teams with cross-functional member rosters.")

        # 6. Create Tags
        tag_arch = Tag(name="Architecture", organization_id=org1.id)
        tag_micro = Tag(name="Microservices", organization_id=org1.id)
        tag_sec = Tag(name="Security", organization_id=org1.id)
        tag_db = Tag(name="Database", organization_id=org1.id)
        tag_fe = Tag(name="Frontend", organization_id=org1.id)
        db.add_all([tag_arch, tag_micro, tag_sec, tag_db, tag_fe])
        db.flush()

        # 7. Create Decisions across all states
        print("[5/5] Creating Decisions, Alternatives, Sequential Approvals & Outcomes...")

        now = datetime.now(timezone.utc)

        # Decision 1: ADR-001 (Approved & In Progress)
        dec1 = Decision(
            title="ADR-001: Migration of Core Monolith to Event-Driven Microservices Architecture",
            problem_statement="Our monolithic Rails backend is causing deployment bottlenecks and single-point-of-failure incidents during peak loads.",
            rationale="Event-driven architecture decouples service domains and enables horizontal elasticity.",
            category="Architecture",
            status=DecisionStatus.APPROVED,
            implementation_status=ImplementationStatus.IN_PROGRESS,
            evaluation_criteria='{"scalability": 40, "maintainability": 30, "cost": 30}',
            organization_id=org1.id,
            created_by=employee_user.id,
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=2),
        )
        dec1.tags.extend([tag_arch, tag_micro])
        db.add(dec1)
        db.flush()

        alt1_1 = Alternative(
            decision_id=dec1.id,
            name="Event-Driven Microservices with Kafka & Go/FastAPI",
            description="Decompose user, billing, and decision services into asynchronous microservices communicating over Kafka pub/sub topic partitions.",
            pros="Independent scaling per service, high fault isolation, zero-downtime micro-deployments, sub-20ms event processing.",
            cons="Requires distributed tracing (OpenTelemetry), eventual consistency handling, and elevated local developer setup.",
            estimated_cost=45000.0,
            risk_level=RiskLevel.MEDIUM,
            feasibility_score=5,
        )
        alt1_2 = Alternative(
            decision_id=dec1.id,
            name="Modular Monolith with Citus PostgreSQL Sharding",
            description="Preserve the unified monolith codebase but reorganize into strictly bounded domain modules and shard database tables with Citus.",
            pros="Simpler deployment artifact, shared in-memory function calls, lower initial architectural overhead.",
            cons="Shared runtime failure domains remain; long-term deployment queue bottlenecks during enterprise releases.",
            estimated_cost=18000.0,
            risk_level=RiskLevel.LOW,
            feasibility_score=4,
        )
        db.add_all([alt1_1, alt1_2])

        # Approvals for Dec 1 (Both stages Approved)
        app1_1 = Approval(
            decision_id=dec1.id,
            reviewer_id=reviewer_user.id,
            sequence_order=1,
            status=ApprovalStatus.APPROVED,
            completed_at=now - timedelta(days=10),
            created_at=now - timedelta(days=12)
        )
        app1_2 = Approval(
            decision_id=dec1.id,
            reviewer_id=sec_reviewer.id,
            sequence_order=2,
            status=ApprovalStatus.APPROVED,
            completed_at=now - timedelta(days=8),
            created_at=now - timedelta(days=10)
        )
        db.add_all([app1_1, app1_2])

        # Comments for Dec 1
        comm1 = Comment(
            decision_id=dec1.id,
            user_id=reviewer_user.id,
            content="Alex, have we conducted load tests simulating 10,000 concurrent decision state writes during failover?",
            created_at=now - timedelta(days=11)
        )
        comm2 = Comment(
            decision_id=dec1.id,
            user_id=employee_user.id,
            content="Yes, Raftaar. k6 benchmarks showed zero packet loss with consumer groups auto-rebalancing in under 4.2 seconds.",
            created_at=now - timedelta(days=11, hours=-2)
        )
        db.add_all([comm1, comm2])

        # Audit Logs for Dec 1
        db.add(AuditLog(decision_id=dec1.id, user_id=employee_user.id, action="CREATE", entity_type="decision", entity_id=dec1.id, description="Decision authored and created.", created_at=now - timedelta(days=14)))
        db.add(AuditLog(decision_id=dec1.id, user_id=reviewer_user.id, action="APPROVE", entity_type="decision", entity_id=dec1.id, description="Stage 1 technical evaluation approved.", created_at=now - timedelta(days=10)))
        db.add(AuditLog(decision_id=dec1.id, user_id=sec_reviewer.id, action="APPROVE", entity_type="decision", entity_id=dec1.id, description="Stage 2 security compliance approved.", created_at=now - timedelta(days=8)))
        db.add(AuditLog(decision_id=dec1.id, user_id=employee_user.id, action="UPDATE", entity_type="decision", entity_id=dec1.id, description="Implementation status set to IN_PROGRESS.", created_at=now - timedelta(days=2)))

        # Decision 2: ADR-002 (Under Active Review - Stage 1 Pending)
        dec2 = Decision(
            title="ADR-002: Zero-Trust Identity & Secrets Management (Vault KMS)",
            problem_statement="Static credentials in config files violate compliance mandates and pose insider threat risks.",
            rationale="HashiCorp Vault provides short-lived dynamic credentials and unified secret governance.",
            category="Security",
            status=DecisionStatus.UNDER_REVIEW,
            implementation_status=ImplementationStatus.NOT_STARTED,
            evaluation_criteria='{"compliance": 50, "dev_experience": 25, "cost": 25}',
            organization_id=org1.id,
            created_by=employee_user.id,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1),
        )
        dec2.tags.extend([tag_sec, tag_arch])
        db.add(dec2)
        db.flush()

        alt2_1 = Alternative(
            decision_id=dec2.id,
            name="HashiCorp Vault Dynamic Ephemeral Credentials with Kubernetes OIDC",
            description="Deploy high-availability HashiCorp Vault cluster. Inject time-limited ephemeral secrets directly into pod memory with automatic token renewal.",
            pros="Zero static credentials in git/env, granular audit trails for every key request, automated cert rotation.",
            cons="Operational overhead of maintaining Consul/Raft storage backend; requires team training on Vault CLI.",
            estimated_cost=28000.0,
            risk_level=RiskLevel.LOW,
            feasibility_score=5,
        )
        alt2_2 = Alternative(
            decision_id=dec2.id,
            name="AWS Secrets Manager with IAM Roles for Service Accounts (IRSA)",
            description="Rely fully on cloud provider native secrets management and IAM role bindings.",
            pros="Fully managed by AWS with 99.99% SLA; zero servers to maintain.",
            cons="Vendor lock-in; higher recurring API call pricing ($0.05 per 10k calls); multi-cloud portability issues.",
            estimated_cost=20000.0,
            risk_level=RiskLevel.LOW,
            feasibility_score=4,
        )
        db.add_all([alt2_1, alt2_2])

        # Sequential Approvals for Dec 2: Raftaar (Stage 1 Pending), Elena (Stage 2 Pending)
        app2_1 = Approval(
            decision_id=dec2.id,
            reviewer_id=reviewer_user.id,
            sequence_order=1,
            status=ApprovalStatus.PENDING,
            due_date=now + timedelta(days=4),
            created_at=now - timedelta(days=3)
        )
        app2_2 = Approval(
            decision_id=dec2.id,
            reviewer_id=sec_reviewer.id,
            sequence_order=2,
            status=ApprovalStatus.PENDING,
            due_date=now + timedelta(days=7),
            created_at=now - timedelta(days=3)
        )
        db.add_all([app2_1, app2_2])

        # Comments for Dec 2
        db.add(Comment(
            decision_id=dec2.id,
            user_id=sec_reviewer.id,
            content="Please ensure the Raft storage volume is encrypted with KMS customer-managed keys (CMK).",
            created_at=now - timedelta(days=2)
        ))

        # Decision 3: ADR-003 (Completed & Outcomes Recorded)
        dec3 = Decision(
            title="ADR-003: Adoption of PostgreSQL 16 as Unified Relational & JSON Datastore",
            problem_statement="Maintaining separate MongoDB and MySQL clusters is causing high sync latency and dual billing.",
            rationale="Modern PostgreSQL 16 handles both relational joins and JSON documents with superior indexing.",
            category="Database",
            status=DecisionStatus.APPROVED,
            implementation_status=ImplementationStatus.COMPLETED,
            final_outcomes="Successfully consolidated 14 service datastores into PostgreSQL 16. JSONB GIN indexing reduced complex search queries from 640ms to 24ms. Eliminated $3,400/month in secondary document database licensing.",
            evaluation_criteria='{"performance": 40, "operational_simplicity": 30, "cost": 30}',
            organization_id=org1.id,
            created_by=sujal_user.id,
            created_at=now - timedelta(days=45),
            updated_at=now - timedelta(days=5),
        )
        dec3.tags.extend([tag_db, tag_arch])
        db.add(dec3)
        db.flush()

        alt3_1 = Alternative(
            decision_id=dec3.id,
            name="PostgreSQL 16 with JSONB Indexing & TimescaleDB Extension",
            description="Use modern PostgreSQL native JSON capabilities and partitioning to replace dedicated NoSQL stores.",
            pros="ACID transactions across structured and unstructured data, mature backup ecosystem (pgBackRest), no license fees.",
            cons="Requires DBA expertise for vacuuming and WAL archiving tuning.",
            estimated_cost=12000.0,
            risk_level=RiskLevel.LOW,
            feasibility_score=5,
        )
        db.add(alt3_1)

        app3_1 = Approval(
            decision_id=dec3.id,
            reviewer_id=reviewer_user.id,
            sequence_order=1,
            status=ApprovalStatus.APPROVED,
            completed_at=now - timedelta(days=40),
            created_at=now - timedelta(days=44)
        )
        db.add(app3_1)

        # Decision 4: ADR-004 (Draft)
        dec4 = Decision(
            title="ADR-004: Standardized Frontend State Architecture (Zustand + React Query)",
            problem_statement="Disparate local state patterns across client apps are causing unnecessary re-renders and developer onboarding friction.",
            rationale="Combining Zustand for client state and TanStack Query for server caching establishes clear boundaries.",
            category="Frontend",
            status=DecisionStatus.DRAFT,
            implementation_status=ImplementationStatus.NOT_STARTED,
            evaluation_criteria='{"bundle_size": 30, "dev_velocity": 40, "learning_curve": 30}',
            organization_id=org1.id,
            created_by=sujal_user.id,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=3),
        )
        dec4.tags.extend([tag_fe])
        db.add(dec4)
        db.flush()

        alt4_1 = Alternative(
            decision_id=dec4.id,
            name="Zustand (Client State) + TanStack React Query (Server Cache)",
            description="Ultra-lightweight state solution eliminating boilerplate and providing automatic request deduplication and background cache invalidation.",
            pros="Zero boilerplate, 1.2kB bundle size, no complex provider wrappers, clean custom hook exports.",
            cons="Requires clear guidelines to separate client-only UI state from server responses.",
            estimated_cost=0.0,
            risk_level=RiskLevel.LOW,
            feasibility_score=5,
        )
        db.add(alt4_1)

        # Decision 5: ADR-005 (Archived)
        dec5 = Decision(
            title="ADR-005: Evaluation of Docker Swarm vs Managed Kubernetes",
            problem_statement="Need a production container orchestration platform for rolling zero-downtime updates.",
            rationale="Kubernetes ecosystem maturity and automated scaling outweigh Swarm simplicity.",
            category="Infrastructure",
            status=DecisionStatus.ARCHIVED,
            implementation_status=ImplementationStatus.COMPLETED,
            final_outcomes="Evaluation concluded. Kubernetes selected for cluster autoscaling and widespread community tooling support. Docker Swarm archived.",
            organization_id=org1.id,
            created_by=employee_user.id,
            created_at=now - timedelta(days=90),
            updated_at=now - timedelta(days=60),
        )
        dec5.tags.extend([tag_arch, tag_micro])
        db.add(dec5)
        db.flush()

        alt5_1 = Alternative(
            decision_id=dec5.id,
            name="Managed Kubernetes (EKS/GKE)",
            description="Container orchestration cluster with autoscaling node groups and Helm deployment charts.",
            pros="Industry standard, rich ecosystem, native service mesh integration.",
            cons="Steeper learning curve and higher baseline cluster cost.",
            estimated_cost=35000.0,
            risk_level=RiskLevel.MEDIUM,
            feasibility_score=5,
        )
        db.add(alt5_1)

        app5_1 = Approval(
            decision_id=dec5.id,
            reviewer_id=reviewer_user.id,
            sequence_order=1,
            status=ApprovalStatus.APPROVED,
            completed_at=now - timedelta(days=80),
            created_at=now - timedelta(days=88)
        )
        db.add(app5_1)

        # 8. Create In-App Notifications
        print(" -> Creating Notifications...")
        notif1 = Notification(
            user_id=reviewer_user.id,
            link=f"/decisions/{dec2.id}",
            notification_type=NotificationType.APPROVAL_REQUESTED,
            title="Review Requested: ADR-002",
            message="Alex Chen requested your Stage 1 architectural evaluation for ADR-002: Zero-Trust Identity & Secrets Management.",
            is_read=False,
            created_at=now - timedelta(days=3)
        )
        notif2 = Notification(
            user_id=employee_user.id,
            link=f"/decisions/{dec1.id}",
            notification_type=NotificationType.DECISION_STATUS_CHANGED,
            title="ADR-001 Approved & Enacted",
            message="ADR-001 (Microservices Architecture) has passed all approval stages and is now marked In Progress.",
            is_read=False,
            created_at=now - timedelta(days=8)
        )
        notif3 = Notification(
            user_id=manager_user.id,
            link=f"/decisions/{dec2.id}",
            notification_type=NotificationType.DECISION_STATUS_CHANGED,
            title="New Decision in Review: ADR-002",
            message="A new high-priority security ADR was submitted for review in Security & Compliance Governance.",
            is_read=True,
            created_at=now - timedelta(days=3)
        )
        db.add_all([notif1, notif2, notif3])

        # Commit everything
        db.commit()

        print("=" * 60)
        print("DATABASE SUCCESSFULLY SEEDED WITH PRISTINE DEMO DATA!")
        print("=" * 60)
        print("\nAll User Accounts (Password for all: 'password123'):")
        print(" 1. Administrator : admin@example.com       (John Doe - CIO)")
        print(" 2. Manager       : manager@example.com     (Sarah Jenkins - VP Eng)")
        print(" 3. Reviewer      : reviewer@example.com    (Raftaar Singh - Principal Architect)")
        print(" 4. Reviewer (Sec): sec_reviewer@example.com(Elena Vance - Security Lead)")
        print(" 5. Employee      : employee@example.com    (Alex Chen - Senior Engineer)")
        print(" 6. Employee      : sujal@example.com       (Sujal Sharma - Fullstack Lead)")
        print("\nDecisions Seeded:")
        print(" - ADR-001: Monolith to Microservices (Approved & In Progress)")
        print(" - ADR-002: Zero-Trust Vault KMS (Under Active Review - Raftaar Pending)")
        print(" - ADR-003: PostgreSQL 16 Unified Datastore (Completed with Outcomes)")
        print(" - ADR-004: Frontend State Architecture (Draft)")
        print(" - ADR-005: Container Orchestrator Selection (Archived)")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Error during clean and seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_seed()
