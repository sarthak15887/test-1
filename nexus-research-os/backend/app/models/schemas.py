from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRoleEnum(str, Enum):
    RESEARCHER = "researcher"
    LAB_ADMIN = "lab_admin"
    ORGANIZATION_ADMIN = "organization_admin"
    SUPER_ADMIN = "super_admin"


class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AgentRunStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    quota_daily_tokens: Optional[int] = None
    quota_monthly_runs: Optional[int] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    settings: Dict[str, Any] = {}
    quota_daily_tokens: int
    quota_monthly_runs: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRoleEnum = UserRoleEnum.RESEARCHER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    organization_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    id: UUID
    organization_id: Optional[UUID]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: List[str] = []


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: UUID
    status: ProjectStatusEnum
    owner_id: UUID
    organization_id: UUID
    settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    document_type: str
    metadata: Dict[str, Any] = {}


class DocumentCreate(DocumentBase):
    project_id: Optional[UUID] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    id: UUID
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    organization_id: UUID
    project_id: Optional[UUID]
    uploaded_by: UUID
    vector_indexed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Agent Run Schemas
class AgentRunBase(BaseModel):
    name: Optional[str] = None
    agent_type: str
    config: Dict[str, Any] = {}
    input_data: Dict[str, Any] = {}


class AgentRunCreate(AgentRunBase):
    project_id: Optional[UUID] = None


class AgentRunUpdate(BaseModel):
    status: Optional[AgentRunStatusEnum] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AgentRunResponse(AgentRunBase):
    id: UUID
    status: AgentRunStatusEnum
    user_id: UUID
    project_id: Optional[UUID]
    organization_id: UUID
    output_data: Dict[str, Any] = {}
    logs: List[Any] = []
    error_message: Optional[str] = None
    tokens_used: int = 0
    duration_seconds: float = 0.0
    cost_usd: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Knowledge Graph Schemas
class KnowledgeNodeBase(BaseModel):
    node_type: str
    label: str = Field(..., min_length=1, max_length=500)
    properties: Dict[str, Any] = {}


class KnowledgeNodeCreate(KnowledgeNodeBase):
    source_document_id: Optional[UUID] = None


class KnowledgeNodeResponse(KnowledgeNodeBase):
    id: UUID
    neo4j_id: str
    organization_id: UUID
    source_document_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search and Query Schemas
class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(10, ge=1, le=100)
    include_vectors: bool = True
    include_graph: bool = True


class SearchResult(BaseModel):
    document_id: Optional[UUID] = None
    node_id: Optional[UUID] = None
    score: float
    content: str
    metadata: Dict[str, Any] = {}
    source_type: str  # "document" or "knowledge_node"
