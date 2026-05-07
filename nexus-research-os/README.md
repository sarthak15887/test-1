# Nexus Research OS - Comprehensive README

## Overview
Nexus Research OS is an advanced, autonomous AI platform designed for scientific research and development. It provides researchers across all major fields with powerful AI tools for literature analysis, experimental design, data analysis, and knowledge discovery.

## Key Features

### 🧠 Multi-Agent AI System
- **Chief Scientist Agent**: Orchestrates complex research workflows
- **Specialized Agents**: Literature review, data analysis, hypothesis generation, experimental design
- **Autonomous Execution**: Agents can plan and execute multi-step research tasks
- **Real-time Monitoring**: WebSocket-based live agent activity streaming

### 📚 Knowledge Management
- **Document Processing**: PDF parsing, chunking, and intelligent indexing
- **Vector Search**: Semantic search across research documents using Qdrant
- **Knowledge Graph**: Neo4j-powered entity extraction and relationship mapping
- **Graph RAG**: Combine vector and graph search for enhanced retrieval

### 💻 Secure Code Sandbox
- **Isolated Execution**: Docker-based containerized code execution
- **Multi-language Support**: Python with extensible language support
- **Resource Limits**: Memory, CPU, and timeout constraints for safety
- **Package Management**: Dynamic package installation in sandboxed environment

### 🔒 Enterprise Security
- **Multi-tenancy**: Organization and project-level isolation
- **RBAC**: Role-based access control
- **Audit Logging**: Comprehensive activity tracking
- **Sandboxed Execution**: No network access, read-only filesystem

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                    │
│  Dashboard | Projects | Knowledge Explorer | Code Sandbox   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 API Gateway (FastAPI + WebSockets)          │
│         /api/v1/agents | /api/v1/knowledge | /sandbox       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Agent Service │  │  Knowledge    │  │   Sandbox     │
│  (LangGraph)  │  │   Pipeline    │  │   Service     │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   PostgreSQL  │  │    Qdrant     │  │    Docker     │
│   (Metadata)  │  │  (Vectors)    │  │  (Sandbox)    │
└───────────────┘  └───────────────┘  └───────────────┘
                          │
                          ▼
                   ┌───────────────┐
                   │     Neo4j     │
                   │  (Knowledge   │
                   │     Graph)    │
                   └───────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Agent Framework**: LangGraph
- **LLM Router**: LiteLLM
- **Database**: PostgreSQL 15 (asyncpg)
- **Vector DB**: Qdrant
- **Graph DB**: Neo4j 5
- **Cache**: Redis 7
- **Task Queue**: Celery + RabbitMQ

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query + Zustand
- **Visualization**: react-force-graph

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + OpenTelemetry

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### 1. Clone Repository
```bash
git clone https://github.com/your-org/nexus-research-os.git
cd nexus-research-os
```

### 2. Configure Environment
```bash
cp backend/.env.example backend/.env
# Edit .env with your API keys and settings
```

### 3. Start Services (Development)
```bash
docker-compose up -d
```

Services available:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- Qdrant Dashboard: http://localhost:6333/dashboard

### 4. Run Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## API Endpoints

### Agents
- `POST /api/v1/agents/run` - Start new agent run
- `GET /api/v1/agents/{run_id}` - Get agent run status
- `GET /api/v1/agents/` - List agent runs
- `DELETE /api/v1/agents/{run_id}` - Cancel agent run
- `WS /api/v1/agents/ws/{run_id}` - WebSocket for real-time monitoring

### Knowledge Graph
- `POST /api/v1/knowledge/process-document` - Process document to graph
- `POST /api/v1/knowledge/search` - Search knowledge graph
- `GET /api/v1/knowledge/stats` - Get graph statistics
- `GET /api/v1/knowledge/entities/{entity_id}` - Get entity details

### Code Sandbox
- `POST /api/v1/sandbox/execute` - Execute code in sandbox
- `GET /api/v1/sandbox/containers` - List active containers
- `POST /api/v1/sandbox/containers/{id}/stop` - Stop container

## Deployment

### Kubernetes Deployment
```bash
# Create namespace and secrets
kubectl apply -f infra/k8s/secrets.yaml
kubectl apply -f infra/k8s/deployment.yaml

# Verify deployment
kubectl get pods -n nexus-research-os
```

### Helm Chart (Coming Soon)
```bash
helm install nexus ./infra/helm/nexus-research-os
```

## Configuration

### Environment Variables

#### Core Settings
- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: Qdrant vector database URL
- `NEO4J_URI`: Neo4j Bolt URI
- `REDIS_URL`: Redis connection string

#### LLM Configuration
- `DEFAULT_LLM_PROVIDER`: openai, anthropic, azure, etc.
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

#### Security
- `SECRET_KEY`: JWT signing key (min 32 chars)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Testing Strategy

### Unit Tests
- Service layer tests
- Utility function tests
- Model validation tests

### Integration Tests
- API endpoint tests
- Database integration tests
- External service mocks

### E2E Tests
- User workflow tests
- Agent execution tests
- Full pipeline tests

## Security Considerations

1. **Code Sandbox**: All user code executes in isolated Docker containers with no network access
2. **API Authentication**: JWT-based authentication with refresh tokens
3. **Data Encryption**: TLS for data in transit, encryption at rest for sensitive data
4. **Rate Limiting**: Configurable rate limits per user/organization
5. **Audit Logging**: All actions logged for compliance and debugging

## Roadmap

### Phase 1 (Completed) ✓
- Core infrastructure
- Basic agent framework
- Document processing
- Knowledge graph foundation

### Phase 2 (In Progress)
- Advanced agent workflows
- Real-time collaboration
- Enhanced UI/UX
- Performance optimization

### Phase 3 (Planned)
- Domain-specific agents (biology, chemistry, physics)
- Lab equipment integration
- Advanced analytics dashboard
- Mobile applications

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

Proprietary - All rights reserved.

## Support

For support and questions:
- Documentation: https://docs.nexusresearch.os
- Email: support@nexusresearch.os
- Discord: https://discord.gg/nexus-research

## Acknowledgments

Built with amazing open-source tools:
- FastAPI
- LangChain/LangGraph
- Next.js
- Qdrant
- Neo4j
