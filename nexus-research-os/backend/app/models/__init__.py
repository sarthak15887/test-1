from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, ForeignKey, Enum, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.core.database import Base


class UserRoleEnum(str, enum.Enum):
    RESEARCHER = "researcher"
    LAB_ADMIN = "lab_admin"
    ORGANIZATION_ADMIN = "organization_admin"
    SUPER_ADMIN = "super_admin"


class ProjectStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AgentRunStatusEnum(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class DocumentTypeEnum(str, enum.Enum):
    PDF = "pdf"
    TXT = "txt"
    MD = "markdown"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    IMAGE = "image"
    OTHER = "other"


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    settings = Column(JSON, default=dict)
    quota_daily_tokens = Column(Integer, default=100000)
    quota_monthly_runs = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="organization", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="organization", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_org_slug', 'slug'),
        Index('idx_org_active', 'is_active'),
    )


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.RESEARCHER, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    metadata = Column(JSON, default=dict)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploaded_by_user", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_org', 'organization_id'),
    )


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.DRAFT, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tags = Column(ARRAY(String), default=list)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_project_owner', 'owner_id'),
        Index('idx_project_org', 'organization_id'),
        Index('idx_project_status', 'status'),
    )


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    document_type = Column(Enum(DocumentTypeEnum), nullable=False)
    file_path = Column(String(1024), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(255), nullable=True)
    metadata = Column(JSON, default=dict)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vector_indexed = Column(Boolean, default=False, nullable=False)
    graph_processed = Column(Boolean, default=False, nullable=False)
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    project = relationship("Project", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="source_document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_doc_org', 'organization_id'),
        Index('idx_doc_project', 'project_id'),
        Index('idx_doc_vector', 'vector_indexed'),
        Index('idx_doc_type', 'document_type'),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    metadata = Column(JSON, default=dict)
    embedding_vector = Column(JSON, nullable=True)  # Store vector as JSON for flexibility
    qdrant_point_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index('idx_chunk_doc', 'document_id'),
        Index('idx_chunk_index', 'chunk_index'),
        UniqueConstraint('document_id', 'chunk_index', name='uq_chunk_doc_index'),
    )


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    node_type = Column(String(100), nullable=False, index=True)
    label = Column(String(500), nullable=False)
    properties = Column(JSON, default=dict)
    neo4j_id = Column(String(255), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="knowledge_nodes")
    source_document = relationship("Document", back_populates="knowledge_nodes")
    relationships_out = relationship("KnowledgeRelationship", foreign_keys="KnowledgeRelationship.source_node_id", back_populates="source_node", cascade="all, delete-orphan")
    relationships_in = relationship("KnowledgeRelationship", foreign_keys="KnowledgeRelationship.target_node_id", back_populates="target_node")
    
    __table_args__ = (
        Index('idx_knowledge_node_type', 'node_type'),
        Index('idx_knowledge_node_org', 'organization_id'),
    )


class KnowledgeRelationship(Base):
    __tablename__ = "knowledge_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    relationship_type = Column(String(100), nullable=False, index=True)
    properties = Column(JSON, default=dict)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    neo4j_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_node = relationship("KnowledgeNode", foreign_keys=[source_node_id], back_populates="relationships_out")
    target_node = relationship("KnowledgeNode", foreign_keys=[target_node_id], back_populates="relationships_in")
    
    __table_args__ = (
        Index('idx_rel_source', 'source_node_id'),
        Index('idx_rel_target', 'target_node_id'),
        Index('idx_rel_type', 'relationship_type'),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=True)
    agent_type = Column(String(100), nullable=False, index=True)
    config = Column(JSON, default=dict)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    status = Column(Enum(AgentRunStatusEnum), default=AgentRunStatusEnum.PENDING, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    logs = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    cost_usd = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="agent_runs")
    project = relationship("Project", back_populates="agent_runs")
    organization = relationship("Organization", back_populates="agent_runs")
    
    __table_args__ = (
        Index('idx_run_user', 'user_id'),
        Index('idx_run_project', 'project_id'),
        Index('idx_run_org', 'organization_id'),
        Index('idx_run_status', 'status'),
        Index('idx_run_created', 'created_at'),
    )


class SandboxSession(Base):
    __tablename__ = "sandbox_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    sandbox_type = Column(String(50), nullable=False)  # docker, firecracker
    status = Column(String(50), default="pending", index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_limit = Column(String(50), default="512m")
    cpu_limit = Column(Float, default=1.0)
    timeout_seconds = Column(Integer, default=120)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent_run = relationship("AgentRun", backref="sandbox_sessions")
    user = relationship("User")
    organization = relationship("Organization")
    
    __table_args__ = (
        Index('idx_sandbox_session', 'session_id'),
        Index('idx_sandbox_status', 'status'),
    )


class WebSocketConnection(Base):
    __tablename__ = "websocket_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    connection_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_heartbeat = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_ws_connection', 'connection_id'),
        Index('idx_ws_user', 'user_id'),
    )
