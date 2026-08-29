import sys, os
sys.path.insert(0, os.path.abspath("."))

import json
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.models.alternative import Alternative, RiskLevel
from app.models.approval import Approval, ApprovalStatus
from app.models.audit import (
    AccessLog,
    AuditAction,
    AuditLog,
    DecisionVersion,
    SecurityLog,
)
from app.models.comment import Comment
from app.models.decision import Decision, DecisionStatus
from app.models.meeting_note import MeetingNote
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.thread import DiscussionThread
from app.models.user import User, UserRole
from app.services.security import hash_password


def seed_database():
    db = SessionLocal()
    try:
        print("--- Starting Database Seeding ---")

        # 1. Organization
        org = db.query(Organization).filter(Organization.id == 1).first()
        if not org:
            org = Organization(
                id=1,
                name="Default Organization",
                description="Primary Enterprise Workspace",
            )
            db.add(org)
            db.flush()
        print(f"Organization: {org.name} (id={org.id})")

        # 2. Fix/Ensure standard users across all 4 roles
        hashed_pwd = hash_password("Password123!")

        users_to_ensure = [
            {
                "email": "admin@example.com",
                "full_name": "Ayush Sharma (Admin)",
                "role": UserRole.ADMINISTRATOR,
                "department": "Engineering",
                "designation": "Head of Engineering",
                "employee_id": "EMP-001",
            },
            {
                "email": "manager@example.com",
                "full_name": "Arjun Mehta (Manager)",
                "role": UserRole.MANAGER,
                "department": "Engineering",
                "designation": "Engineering Manager",
                "employee_id": "EMP-002",
            },
            {
                "email": "reviewer@example.com",
                "full_name": "Sneha Patel (Reviewer)",
                "role": UserRole.REVIEWER,
                "department": "Engineering",
                "designation": "Principal Architect",
                "employee_id": "EMP-003",
            },
            {
                "email": "employee@example.com",
                "full_name": "Ankush Verma (Employee)",
                "role": UserRole.EMPLOYEE,
                "department": "Engineering",
                "designation": "Senior Backend Developer",
                "employee_id": "EMP-004",
            },
        ]

        user_map = {}
        for u_data in users_to_ensure:
            u = db.query(User).filter(User.email == u_data["email"]).first()
            if not u:
                u = User(
                    email=u_data["email"],
                    full_name=u_data["full_name"],
                    role=u_data["role"],
                    password=hashed_pwd,
                    organization_id=org.id,
                    department=u_data["department"],
                    designation=u_data["designation"],
                    employee_id=u_data["employee_id"],
                )
                db.add(u)
                db.flush()
            else:
                u.organization_id = org.id
                u.password = hashed_pwd
                u.department = u_data["department"]
            user_map[u.role] = u

        # Also update any other existing users to belong to org 1
        for existing_u in db.query(User).all():
            if existing_u.organization_id is None:
                existing_u.organization_id = org.id
            if existing_u.password.startswith("123456") or len(existing_u.password) < 20:
                existing_u.password = hashed_pwd

        db.flush()
        print(f"Users configured. Total users: {db.query(User).count()}")

        admin_user = user_map[UserRole.ADMINISTRATOR]
        manager_user = user_map[UserRole.MANAGER]
        reviewer_user = user_map[UserRole.REVIEWER]
        employee_user = user_map[UserRole.EMPLOYEE]

        # 3. Fix existing decisions: set organization_id=1 and create Version 1 if missing
        for d in db.query(Decision).all():
            if d.organization_id is None:
                d.organization_id = org.id
            # Ensure version 1 exists
            v1 = (
                db.query(DecisionVersion)
                .filter(
                    DecisionVersion.decision_id == d.id,
                    DecisionVersion.version_number == 1,
                )
                .first()
            )
            if not v1:
                v1 = DecisionVersion(
                    decision_id=d.id,
                    version_number=1,
                    title=d.title,
                    problem_statement=d.problem_statement,
                    rationale=d.rationale,
                    category=d.category,
                    status=d.status.value if hasattr(d.status, "value") else str(d.status),
                    created_by=d.created_by if d.created_by else employee_user.id,
                    created_at=d.created_at,
                )
                db.add(v1)

        db.flush()

        # 4. Tags
        tags_data = [
            "PostgreSQL",
            "Database",
            "Backend",
            "Infrastructure",
            "Cloud",
            "Kafka",
            "Architecture",
            "Finance",
            "Billing",
            "Stripe",
            "Integration",
            "Security",
            "ZeroTrust",
            "Okta",
            "Operations",
            "CustomerSupport",
            "AI",
            "Zendesk",
            "Legacy",
            "Deprecation",
        ]

        tag_objs = {}
        for tag_name in tags_data:
            t = (
                db.query(Tag)
                .filter(
                    Tag.name == tag_name,
                    Tag.organization_id == org.id,
                )
                .first()
            )
            if not t:
                t = Tag(
                    name=tag_name,
                    organization_id=org.id,
                )
                db.add(t)
                db.flush()
            tag_objs[tag_name] = t

        print(f"Tags configured. Total tags: {db.query(Tag).count()}")

        # 5. Populate 5 Rich Decisions
        new_decisions_data = [
            {
                "title": "Adopt Event-Driven Architecture with Apache Kafka",
                "category": "Technology",
                "status": DecisionStatus.APPROVED,
                "problem_statement": "Synchronous REST microservices suffer latency spikes and cascading failures under heavy load. A resilient asynchronous event backbone is required.",
                "rationale": "Apache Kafka provides high throughput (100k+ msg/sec), partition-level ordering, distributed log retention, and replay capabilities across services.",
                "creator": employee_user,
                "tags": ["Kafka", "Architecture", "Backend", "Infrastructure", "Database"],
                "created_days_ago": 20,
                "alternatives": [
                    {
                        "name": "Apache Kafka Event Cluster",
                        "description": "Distributed event streaming platform with multi-broker cluster and KRaft consensus.",
                        "pros": "Ultra high throughput, durable log retention, event replay, strong ecosystem.",
                        "cons": "Requires cluster monitoring, steeper learning curve.",
                        "cost": 1500.00,
                        "feasibility": 5,
                        "risk": RiskLevel.MEDIUM,
                    },
                    {
                        "name": "RabbitMQ Message Broker",
                        "description": "AMQP message broker with flexible routing and dead-letter queues.",
                        "pros": "Simple setup, rich AMQP routing features, management UI.",
                        "cons": "Lower throughput for multi-terabyte log retention and replay.",
                        "cost": 900.00,
                        "feasibility": 4,
                        "risk": RiskLevel.LOW,
                    },
                    {
                        "name": "AWS SQS & SNS",
                        "description": "Fully managed pub/sub messaging queue on AWS.",
                        "pros": "Zero operational maintenance, elastic auto-scaling.",
                        "cons": "Vendor lock-in, limited historical replay capability.",
                        "cost": 2100.00,
                        "feasibility": 4,
                        "risk": RiskLevel.MEDIUM,
                    },
                ],
                "threads": [
                    {
                        "title": "Benchmarking Throughput & Latency",
                        "comments": [
                            "We ran load tests with 50,000 events/sec. Kafka sustained p99 latency under 12ms.",
                            "Benchmarks look excellent. Kafka handles consumer lag recovery much cleaner than RabbitMQ.",
                        ],
                    }
                ],
                "meeting_notes": [
                    "Architecture Review - Event streaming architecture unanimously endorsed by lead engineers."
                ],
                "approval": {
                    "reviewer": reviewer_user,
                    "status": ApprovalStatus.APPROVED,
                },
                "versions": [
                    {
                        "version_number": 1,
                        "title": "Evaluate Message Brokers for Microservices",
                        "problem_statement": "Need an asynchronous message queue for services.",
                        "rationale": "Initial proposal to evaluate messaging frameworks.",
                        "status": "Draft",
                    },
                    {
                        "version_number": 2,
                        "title": "Adopt Event-Driven Architecture with Apache Kafka",
                        "problem_statement": "Synchronous REST microservices suffer latency spikes and cascading failures under heavy load. A resilient asynchronous event backbone is required.",
                        "rationale": "Kafka benchmarked 50k req/sec with p99 under 12ms.",
                        "status": "Under Review",
                    },
                    {
                        "version_number": 3,
                        "title": "Adopt Event-Driven Architecture with Apache Kafka",
                        "problem_statement": "Synchronous REST microservices suffer latency spikes and cascading failures under heavy load. A resilient asynchronous event backbone is required.",
                        "rationale": "Apache Kafka provides high throughput (100k+ msg/sec), partition-level ordering, distributed log retention, and replay capabilities across services.",
                        "status": "Approved",
                    },
                ],
            },
            {
                "title": "Migrate Financial Reporting to Stripe & QuickBooks",
                "category": "Finance",
                "status": DecisionStatus.UNDER_REVIEW,
                "problem_statement": "Manual reconciliation of multi-currency subscription invoices takes 4 business days each month and introduces audit risk.",
                "rationale": "Automating Stripe Billing webhooks and syncing directly with QuickBooks reduces monthly close time to 2 hours with 100% audit accuracy.",
                "creator": employee_user,
                "tags": ["Finance", "Billing", "Stripe", "Integration", "Operations"],
                "created_days_ago": 12,
                "alternatives": [
                    {
                        "name": "Stripe Billing + QuickBooks Online Sync",
                        "description": "Automated recurring billing sync with bidirectional ledger posting.",
                        "pros": "Automated revenue recognition, tax calculation, self-service customer portal.",
                        "cons": "Stripe billing add-on percentage fees.",
                        "cost": 3200.00,
                        "feasibility": 5,
                        "risk": RiskLevel.LOW,
                    },
                    {
                        "name": "NetSuite ERP Integration",
                        "description": "Full-scale enterprise resource planning implementation.",
                        "pros": "Comprehensive multi-entity accounting and audit compliance.",
                        "cons": "Heavy implementation timeline (6 months) and high license cost.",
                        "cost": 24000.00,
                        "feasibility": 2,
                        "risk": RiskLevel.HIGH,
                    },
                ],
                "threads": [
                    {
                        "title": "SOC2 & PCI Compliance Verification",
                        "comments": [
                            "Verified that Stripe handles all PCI-DSS cardholder data scope off-premises.",
                            "Accounting team approved the QuickBooks general ledger mapping template.",
                        ],
                    }
                ],
                "meeting_notes": [
                    "Finance Steering Meeting: Approved proceeding with Stripe Billing migration pending manager sign-off."
                ],
                "approval": {
                    "reviewer": manager_user,
                    "status": ApprovalStatus.PENDING,
                },
                "versions": [
                    {
                        "version_number": 1,
                        "title": "Automate Monthly Financial Close",
                        "problem_statement": "Manual reconciliation is taking 4 business days.",
                        "rationale": None,
                        "status": "Draft",
                    },
                    {
                        "version_number": 2,
                        "title": "Migrate Financial Reporting to Stripe & QuickBooks",
                        "problem_statement": "Manual reconciliation of multi-currency subscription invoices takes 4 business days each month and introduces audit risk.",
                        "rationale": "Automating Stripe Billing webhooks and syncing directly with QuickBooks reduces monthly close time to 2 hours with 100% audit accuracy.",
                        "status": "Under Review",
                    },
                ],
            },
            {
                "title": "Implement Zero-Trust Security & MFA with Okta",
                "category": "Security",
                "status": DecisionStatus.APPROVED,
                "problem_statement": "Remote distributed teams require centralized single sign-on (SSO), adaptive multi-factor authentication (MFA), and automated SCIM user lifecycle management.",
                "rationale": "Okta provides turnkey SAML/OIDC SSO, risk-based adaptive MFA, and deep integration with AWS IAM and Google Workspace.",
                "creator": employee_user,
                "tags": ["Security", "ZeroTrust", "Okta", "Backend", "Technology"],
                "created_days_ago": 15,
                "alternatives": [
                    {
                        "name": "Okta Workforce Identity Cloud",
                        "description": "Cloud-native IAM suite with adaptive MFA, Universal Directory, and Lifecycle Management.",
                        "pros": "Extensive catalog of 7,000+ app connectors, robust security compliance certifications.",
                        "cons": "Higher annual per-seat licensing.",
                        "cost": 6000.00,
                        "feasibility": 5,
                        "risk": RiskLevel.LOW,
                    },
                    {
                        "name": "Self-Hosted Keycloak Cluster",
                        "description": "Open-source identity and access management server deployed on Kubernetes.",
                        "pros": "Zero licensing fees, complete data sovereignty.",
                        "cons": "Significant maintenance burden, complex HA configuration, self-managed security patches.",
                        "cost": 2200.00,
                        "feasibility": 3,
                        "risk": RiskLevel.HIGH,
                    },
                ],
                "threads": [
                    {
                        "title": "MFA Rollout Strategy & Phasing",
                        "comments": [
                            "Phase 1: IT & Engineering teams (Week 1). Phase 2: Company-wide mandatory enforcement (Week 3).",
                            "FIDO2 WebAuthn security keys will be distributed to production administrators.",
                        ],
                    }
                ],
                "meeting_notes": [
                    "Security Board Review: Zero-trust architecture approved for immediate rollout."
                ],
                "approval": {
                    "reviewer": reviewer_user,
                    "status": ApprovalStatus.APPROVED,
                },
                "versions": [
                    {
                        "version_number": 1,
                        "title": "Upgrade Company Authentication Infrastructure",
                        "problem_statement": "Need MFA for remote workers.",
                        "rationale": None,
                        "status": "Draft",
                    },
                    {
                        "version_number": 2,
                        "title": "Implement Zero-Trust Security & MFA with Okta",
                        "problem_statement": "Remote distributed teams require centralized single sign-on (SSO), adaptive multi-factor authentication (MFA), and automated SCIM user lifecycle management.",
                        "rationale": "Okta evaluated against Keycloak; Okta selected for lower operational overhead.",
                        "status": "Under Review",
                    },
                    {
                        "version_number": 3,
                        "title": "Implement Zero-Trust Security & MFA with Okta",
                        "problem_statement": "Remote distributed teams require centralized single sign-on (SSO), adaptive multi-factor authentication (MFA), and automated SCIM user lifecycle management.",
                        "rationale": "Okta provides turnkey SAML/OIDC SSO, risk-based adaptive MFA, and deep integration with AWS IAM and Google Workspace.",
                        "status": "Approved",
                    },
                ],
            },
            {
                "title": "Transition Customer Support to AI-Assisted Zendesk Workflow",
                "category": "Operations",
                "status": DecisionStatus.DRAFT,
                "problem_statement": "Customer support inbound volume grew by 140% QoQ, driving first-response resolution times above our 4-hour SLA.",
                "rationale": "Deploying generative AI ticket deflection and smart auto-tagging will resolve 35% of tier-1 inquiries automatically and assist agents with drafts.",
                "creator": employee_user,
                "tags": ["Operations", "CustomerSupport", "AI", "Zendesk"],
                "created_days_ago": 5,
                "alternatives": [
                    {
                        "name": "Zendesk Advanced AI Suite",
                        "description": "Pre-trained customer service LLM agents with automated macro generation.",
                        "pros": "Seamless native Zendesk integration, sentiment detection, intent triage.",
                        "cons": "Add-on fee per resolved conversation.",
                        "cost": 3400.00,
                        "feasibility": 5,
                        "risk": RiskLevel.LOW,
                    },
                    {
                        "name": "Intercom Fin AI Copilot",
                        "description": "Conversational AI support bot powered by GPT-4.",
                        "pros": "Outstanding chat deflection and conversational accuracy.",
                        "cons": "Requires migrating existing email ticketing workflow.",
                        "cost": 4800.00,
                        "feasibility": 3,
                        "risk": RiskLevel.MEDIUM,
                    },
                ],
                "threads": [
                    {
                        "title": "SLA & Customer Satisfaction Metrics",
                        "comments": [
                            "Goal is to bring median response time under 15 minutes for premium tier customers.",
                        ],
                    }
                ],
                "meeting_notes": [
                    "Operations Sync: Trialing Zendesk AI in sandbox environment for 2 weeks."
                ],
                "approval": None,
                "versions": [
                    {
                        "version_number": 1,
                        "title": "Transition Customer Support to AI-Assisted Zendesk Workflow",
                        "problem_statement": "Customer support inbound volume grew by 140% QoQ, driving first-response resolution times above our 4-hour SLA.",
                        "rationale": "Deploying generative AI ticket deflection and smart auto-tagging will resolve 35% of tier-1 inquiries automatically and assist agents with drafts.",
                        "status": "Draft",
                    }
                ],
            },
            {
                "title": "Deprecate Legacy Monolith Billing Service",
                "category": "Technology",
                "status": DecisionStatus.ARCHIVED,
                "problem_statement": "The legacy v1 monolithic PHP billing worker is obsolete and all customer subscriptions have migrated to the Stripe microservice.",
                "rationale": "After 90 days of zero ingress traffic and final database archival, the monolith billing daemon has been officially decommissioned.",
                "creator": employee_user,
                "tags": ["Legacy", "Deprecation", "Backend", "Technology", "Infrastructure"],
                "created_days_ago": 45,
                "alternatives": [
                    {
                        "name": "Immediate Decommission & Cold Storage Archive",
                        "description": "Take final SQL dump, store in AWS Glacier, and terminate server instances.",
                        "pros": "Saves $850/mo server costs, eliminates vulnerability surface.",
                        "cons": "None remaining.",
                        "cost": 0.00,
                        "feasibility": 5,
                        "risk": RiskLevel.LOW,
                    }
                ],
                "threads": [
                    {
                        "title": "Traffic Verification & Sunset Checklist",
                        "comments": [
                            "Confirmed zero HTTP requests over the past 30 consecutive days.",
                            "Final encrypted database snapshot uploaded to S3 Glacier Vault.",
                        ],
                    }
                ],
                "meeting_notes": [
                    "Monolith Sunset Meeting: All stakeholders confirmed successful migration."
                ],
                "approval": {
                    "reviewer": manager_user,
                    "status": ApprovalStatus.APPROVED,
                },
                "versions": [
                    {
                        "version_number": 1,
                        "title": "Plan Deprecation of Legacy Monolith Billing",
                        "problem_statement": "Need plan to sunset old billing worker.",
                        "rationale": "Planning phase for decommissioning.",
                        "status": "Under Review",
                    },
                    {
                        "version_number": 2,
                        "title": "Deprecate Legacy Monolith Billing Service",
                        "problem_statement": "The legacy v1 monolithic PHP billing worker is obsolete and all customer subscriptions have migrated to the Stripe microservice.",
                        "rationale": "After 90 days of zero ingress traffic and final database archival, the monolith billing daemon has been officially decommissioned.",
                        "status": "Archived",
                    },
                ],
            },
        ]

        # Insert new decisions if not already present
        for dec_item in new_decisions_data:
            existing = (
                db.query(Decision)
                .filter(
                    Decision.title == dec_item["title"],
                    Decision.organization_id == org.id,
                )
                .first()
            )
            if existing:
                print(f"Decision '{dec_item['title']}' already exists (id={existing.id}). Skipping.")
                continue

            created_time = datetime.utcnow() - timedelta(days=dec_item["created_days_ago"])

            d = Decision(
                title=dec_item["title"],
                problem_statement=dec_item["problem_statement"],
                rationale=dec_item["rationale"],
                category=dec_item["category"],
                status=dec_item["status"],
                created_by=dec_item["creator"].id,
                organization_id=org.id,
                created_at=created_time,
                updated_at=created_time + timedelta(days=2),
            )
            db.add(d)
            db.flush()

            # Tags
            for tname in dec_item["tags"]:
                if tname in tag_objs:
                    d.tags.append(tag_objs[tname])

            # Audit log for creation
            audit_create = AuditLog(
                decision_id=d.id,
                user_id=d.created_by,
                action=AuditAction.CREATE.value,
                entity_type="Decision",
                entity_id=d.id,
                description=f"Decision '{d.title}' was created",
                created_at=created_time,
            )
            db.add(audit_create)

            # Alternatives
            for alt_data in dec_item["alternatives"]:
                alt = Alternative(
                    decision_id=d.id,
                    name=alt_data["name"],
                    description=alt_data["description"],
                    pros=alt_data["pros"],
                    cons=alt_data["cons"],
                    estimated_cost=alt_data["cost"],
                    feasibility_score=alt_data["feasibility"],
                    risk_level=alt_data["risk"],
                    created_at=created_time + timedelta(hours=2),
                )
                db.add(alt)
                db.flush()

                audit_alt = AuditLog(
                    decision_id=d.id,
                    user_id=d.created_by,
                    action=AuditAction.CREATE.value,
                    entity_type="Alternative",
                    entity_id=alt.id,
                    description=f"Alternative '{alt.name}' was created for decision '{d.title}'",
                    created_at=created_time + timedelta(hours=2),
                )
                db.add(audit_alt)

            # Threads & Comments
            for thr_data in dec_item.get("threads", []):
                thr = DiscussionThread(
                    decision_id=d.id,
                    created_by=d.created_by,
                    title=thr_data["title"],
                    created_at=created_time + timedelta(hours=4),
                )
                db.add(thr)
                db.flush()

                for ctext in thr_data["comments"]:
                    cmt = Comment(
                        decision_id=d.id,
                        user_id=reviewer_user.id,
                        thread_id=thr.id,
                        content=ctext,
                        created_at=created_time + timedelta(hours=5),
                    )
                    db.add(cmt)
                    db.flush()

            # Meeting Notes
            for mtext in dec_item.get("meeting_notes", []):
                mn = MeetingNote(
                    decision_id=d.id,
                    created_by=manager_user.id,
                    title="Architecture Alignment Meeting",
                    content=mtext,
                    meeting_date=(created_time + timedelta(hours=8)).date(),
                    created_at=created_time + timedelta(hours=8),
                )
                db.add(mn)
                db.flush()

            # Approval
            if dec_item.get("approval"):
                app_info = dec_item["approval"]
                app_obj = Approval(
                    decision_id=d.id,
                    reviewer_id=app_info["reviewer"].id,
                    status=app_info["status"],
                    created_at=created_time + timedelta(days=1),
                    completed_at=(
                        created_time + timedelta(days=1, hours=4)
                        if app_info["status"] != ApprovalStatus.PENDING
                        else None
                    ),
                )
                db.add(app_obj)
                db.flush()

                audit_app = AuditLog(
                    decision_id=d.id,
                    user_id=app_info["reviewer"].id,
                    action=AuditAction.APPROVE.value if app_info["status"] == ApprovalStatus.APPROVED else AuditAction.CREATE.value,
                    entity_type="Approval",
                    entity_id=app_obj.id,
                    description=f"Approval for '{d.title}' was marked {app_info['status'].value}",
                    created_at=created_time + timedelta(days=1, hours=4),
                )
                db.add(audit_app)

            # Versions
            for v_data in dec_item.get("versions", []):
                v_obj = DecisionVersion(
                    decision_id=d.id,
                    version_number=v_data["version_number"],
                    title=v_data["title"],
                    problem_statement=v_data["problem_statement"],
                    rationale=v_data.get("rationale"),
                    category=d.category,
                    status=v_data["status"],
                    created_by=d.created_by,
                    created_at=created_time + timedelta(days=v_data["version_number"] - 1),
                )
                db.add(v_obj)

            print(f"Created Decision '{d.title}' (id={d.id})")

        # 6. Add some security logs and access logs
        sec_logs = [
            SecurityLog(
                user_id=admin_user.id,
                email=admin_user.email,
                event_type="LOGIN_SUCCESS",
                description=f"Administrator '{admin_user.email}' logged in successfully",
                ip_address="127.0.0.1",
                created_at=datetime.utcnow() - timedelta(hours=3),
            ),
            SecurityLog(
                user_id=employee_user.id,
                email=employee_user.email,
                event_type="LOGIN_SUCCESS",
                description=f"Employee '{employee_user.email}' logged in successfully",
                ip_address="127.0.0.1",
                created_at=datetime.utcnow() - timedelta(hours=2),
            ),
            SecurityLog(
                user_id=None,
                email="unknown_hacker@test.com",
                event_type="LOGIN_FAILED",
                description="Failed login attempt for non-existent email 'unknown_hacker@test.com'",
                ip_address="192.168.1.105",
                created_at=datetime.utcnow() - timedelta(hours=1),
            ),
        ]
        for sl in sec_logs:
            db.add(sl)

        access_logs = [
            AccessLog(
                user_id=admin_user.id,
                resource_type="AuditLog",
                resource_id=None,
                action="VIEW_ALL",
                ip_address="127.0.0.1",
                created_at=datetime.utcnow() - timedelta(minutes=45),
            ),
            AccessLog(
                user_id=employee_user.id,
                resource_type="Decision",
                resource_id=1,
                action="VIEW",
                ip_address="127.0.0.1",
                created_at=datetime.utcnow() - timedelta(minutes=30),
            ),
        ]
        for al in access_logs:
            db.add(al)

        db.commit()
        print("--- Database Seeding Completed Successfully ---")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
