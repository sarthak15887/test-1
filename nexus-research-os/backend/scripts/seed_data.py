"""Seed database with initial data for development and testing."""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.base import Base
from models.organization import Organization
from models.project import Project
from models.document import Document
from models.agent_run import AgentRun
from models.knowledge_graph import Entity, Relationship
from config.database import get_database_url
from security import get_password_hash


async def seed_data():
    """Seed the database with initial test data."""
    database_url = get_database_url()
    
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM organizations"))
        count = result.scalar()
        if count > 0:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create default organization
        org_id = uuid.uuid4()
        org = Organization(
            id=org_id,
            name="Default Research Lab",
            slug="default-lab",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(org)
        await session.flush()
        print(f"Created organization: {org.name}")
        
        # Create admin user
        admin_id = uuid.uuid4()
        admin = OrganizationMember(
            id=admin_id,
            organization_id=org_id,
            email="admin@nexus-research.io",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role="ADMIN",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(admin)
        await session.flush()
        print(f"Created admin user: {admin.email}")
        
        # Create researcher user
        researcher_id = uuid.uuid4()
        researcher = OrganizationMember(
            id=researcher_id,
            organization_id=org_id,
            email="researcher@nexus-research.io",
            hashed_password=get_password_hash("researcher123"),
            full_name="Dr. Jane Smith",
            role="RESEARCHER",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(researcher)
        await session.flush()
        print(f"Created researcher user: {researcher.email}")
        
        # Create sample project
        project_id = uuid.uuid4()
        project = Project(
            id=project_id,
            organization_id=org_id,
            name="Drug Discovery Pipeline",
            description="AI-assisted drug discovery research project",
            created_by=researcher_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(project)
        await session.flush()
        print(f"Created project: {project.name}")
        
        # Create sample agent run
        agent_run_id = uuid.uuid4()
        agent_run = AgentRun(
            id=agent_run_id,
            project_id=project_id,
            user_id=researcher_id,
            objective="Identify potential drug candidates for Alzheimer's disease",
            status="COMPLETED",
            result="Analysis complete. Identified 5 promising compounds with high binding affinity.",
            metadata_={
                "duration_seconds": 245,
                "tokens_used": 15000,
                "models_used": ["gpt-4", "claude-3-opus"]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        session.add(agent_run)
        await session.flush()
        print(f"Created agent run: {agent_run.objective[:50]}...")
        
        # Commit all changes
        await session.commit()
        print("Database seeding completed successfully!")
        print("\nLogin credentials:")
        print("  Admin: admin@nexus-research.io / admin123")
        print("  Researcher: researcher@nexus-research.io / researcher123")


if __name__ == "__main__":
    asyncio.run(seed_data())
