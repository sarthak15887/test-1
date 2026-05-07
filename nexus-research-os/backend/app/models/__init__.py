from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """User roles in the system."""
    RESEARCHER = "researcher"
    LAB_ADMIN = "lab_admin"
    ORGANIZATION_ADMIN = "organization_admin"
    SUPER_ADMIN = "super_admin"


class ProjectStatus(enum.Enum):
    """Project lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AgentRunStatus(enum.Enum):
    """Status of agent execution runs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Organization(Base):
    """Organization model for multi-tenancy."""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    settings = Column(JSONB, default=dict)
    quota_daily_tokens = Column(Integer, default=100000)
    quota_monthly_runs = Column(Integer, default=1000)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    documents = relationship("Document", back_populates="organization")


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.RESEARCHER, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="owner")
    agent_runs = relationship("AgentRun", back_populates="user")


class Project(Base):
    """Research project model."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    settings = Column(JSONB, default=dict)
    tags = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    agent_runs = relationship("AgentRun", back_populates="project")


class Document(Base):
    """Document model for research papers, notes, and data."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=False)  # paper, note, dataset, protocol
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    metadata = Column(JSONB, default=dict)
    vector_indexed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    project = relationship("Project", back_populates="documents")


class AgentRun(Base):
    """Agent execution run model."""
    __tablename__ = "agent_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    status = Column(Enum(AgentRunStatus), default=AgentRunStatus.PENDING, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Agent configuration
    agent_type = Column(String(100), nullable=False)
    config = Column(JSONB, default=dict)
    
    # Execution details
    input_data = Column(JSONB, default=dict)
    output_data = Column(JSONB, default=dict)
    logs = Column(JSONB, default=list)
    error_message = Column(Text, nullable=True)
    
    # Resource tracking
    tokens_used = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    cost_usd = Column(Float, default=0.0)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="agent_runs")
    project = relationship("Project", back_populates="agent_runs")


class KnowledgeNode(Base):
    """Knowledge graph node model."""
    __tablename__ = "knowledge_nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    neo4j_id = Column(String(255), nullable=False, index=True)  # Reference to Neo4j node ID
    node_type = Column(String(100), nullable=False)  # concept, entity, hypothesis, etc.
    label = Column(String(500), nullable=False)
    properties = Column(JSONB, default=dict)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_document = relationship("Document")
