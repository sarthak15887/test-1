# Nexus Research OS - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [API Reference](#api-reference)
5. [Deployment Guide](#deployment-guide)
6. [Operations Manual](#operations-manual)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

## Overview

Nexus Research OS is an enterprise-grade autonomous AI platform designed for scientific research and development. It provides multi-agent orchestration, knowledge graph extraction, secure code execution, and advanced RAG capabilities.

### Key Features
- **Multi-Agent Orchestration**: Autonomous AI agents for complex research tasks
- **Knowledge Graph Engine**: Automatic entity extraction and relationship mapping
- **Secure Code Sandbox**: Isolated Docker/Firecracker execution environment
- **Document Processing**: PDF parsing, OCR, virus scanning, semantic chunking
- **Real-time Monitoring**: WebSocket-based live agent tracking
- **Enterprise Security**: RBAC, multi-tenancy, audit logging

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Projects │ │ Knowledge│ │  Agent   │ │  Sandbox │       │
│  │  Dashboard│ │ Explorer │ │ Monitor  │ │  Editor  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS / WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   Auth   │ │  Agents  │ │ Documents│ │Knowledge │       │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  PostgreSQL   │  │    Qdrant     │  │     Neo4j     │
│  (Primary DB) │  │  (Vector DB)  │  │ (Graph DB)    │
└───────────────┘  └───────────────┘  └───────────────┘
        │
        ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│    Redis      │  │   RabbitMQ    │  │   ClamAV      │
│   (Cache)     │  │  (Message Q)  │  │(Virus Scan)   │
└───────────────┘  └───────────────┘  └───────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11+, FastAPI, SQLAlchemy (Async)
- LangGraph for agent orchestration
- LiteLLM for multi-provider LLM routing
- spaCy for NLP entity extraction

**Frontend:**
- Next.js 14, TypeScript, Tailwind CSS
- React Query, Zustand for state management
- D3.js for knowledge graph visualization
- Monaco Editor for code sandbox

**Infrastructure:**
- PostgreSQL 15, Qdrant, Neo4j
- Redis, RabbitMQ
- Docker, Kubernetes, Helm
- Prometheus, Grafana, OpenTelemetry

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Kubernetes cluster (for production)
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/nexus-research-os.git
cd nexus-research-os
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Run database migrations:**
```bash
./scripts/migrate.sh
```

5. **Seed initial data:**
```bash
./scripts/seed.sh
```

6. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Grafana: http://localhost:3001
- Swagger Docs: http://localhost:8000/docs

### Default Credentials
- Admin: `admin@nexus-research.io` / `admin123`
- Researcher: `researcher@nexus-research.io` / `researcher123`

## API Reference

### Authentication

**POST /api/v1/auth/login**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Agent Runs

**POST /api/v1/agent-runs**
```json
{
  "project_id": "uuid",
  "objective": "Analyze protein structures for drug binding",
  "agent_config": {
    "max_iterations": 10,
    "models": ["gpt-4", "claude-3-opus"]
  }
}
```

**GET /api/v1/agent-runs/{run_id}**
Returns agent run status and results.

**WS /api/v1/ws/agent-runs/{run_id}**
WebSocket endpoint for real-time updates.

### Documents

**POST /api/v1/documents/upload**
Multipart form upload with virus scanning.

**GET /api/v1/documents/{doc_id}/chunks**
Retrieve document chunks for RAG.

### Knowledge Graph

**GET /api/v1/knowledge-graph/entities**
Query extracted entities with filters.

**GET /api/v1/knowledge-graph/relationships**
Query relationships between entities.

## Deployment Guide

### Kubernetes Deployment

1. **Install Helm charts:**
```bash
helm install nexus ./kubernetes/helm/nexus-research-os \
  --namespace nexus \
  --create-namespace \
  -f values-production.yaml
```

2. **Configure ingress:**
Update `values.yaml` with your domain and TLS certificates.

3. **Scale services:**
```bash
kubectl scale deployment nexus-backend --replicas=5
```

### Environment Configuration

**Production Settings:**
- Enable RBAC and network policies
- Configure external database
- Set up secrets management (Vault/AWS Secrets Manager)
- Enable audit logging
- Configure backup schedules

### Monitoring Setup

1. Import Grafana dashboards from `observability/grafana/dashboards/`
2. Configure alerting rules in Prometheus
3. Set up notification channels (Slack, PagerDuty)

## Operations Manual

### Database Migrations

```bash
# Create new migration
cd backend && alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Procedures

**Database Backup:**
```bash
pg_dump -h postgres -U nexus nexus_db > backup_$(date +%Y%m%d).sql
```

**Volume Snapshots:**
Configure Kubernetes VolumeSnapshot resources for persistent volumes.

### Disaster Recovery

1. Restore database from backup
2. Recreate Kubernetes resources
3. Verify data integrity
4. Update DNS if needed

### Scaling Guidelines

**Horizontal Pod Autoscaling:**
- CPU threshold: 70%
- Memory threshold: 80%
- Min replicas: 3
- Max replicas: 20

**Database Optimization:**
- Connection pooling: 20 connections
- Query caching with Redis
- Regular VACUUM ANALYZE

## Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-tenancy with logical isolation

### Network Security
- Zero-trust network policies
- TLS everywhere (mTLS for service mesh)
- WAF configuration

### Data Security
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII redaction in logs
- Secure secret management

### Compliance
- GDPR data retention policies
- HIPAA-ready architecture
- SOC 2 audit trails
- Immutable audit logging

## Troubleshooting

### Common Issues

**Agent runs stuck in PENDING:**
- Check RabbitMQ connectivity
- Verify worker pods are running
- Review resource quotas

**High API latency:**
- Check database connection pool
- Review slow query logs
- Scale backend horizontally

**Virus scanner failures:**
- Verify ClamAV service health
- Check file size limits
- Review network policies

### Logs Access

```bash
# Backend logs
kubectl logs -f deployment/nexus-backend

# Agent worker logs
kubectl logs -f deployment/nexus-agent-worker

# Search logs
kubectl logs deployment/nexus-backend | grep "error"
```

### Metrics Debugging

Access Prometheus at http://prometheus.local to query metrics:
- `rate(http_requests_total[5m])` - Request rate
- `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` - P95 latency
- `agent_runs_total{status="failed"}` - Failed runs

### Support

For additional support:
- GitHub Issues: https://github.com/your-org/nexus-research-os/issues
- Documentation: https://docs.nexus-research.io
- Email: support@nexus-research.io
