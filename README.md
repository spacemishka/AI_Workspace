# AI Workspace

Privacy-first, local AI assistant running on consumer hardware.

## Quick Start

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend
- NVIDIA Container Toolkit (for GPU support with Ollama)
- Git

### 2. Setup

```bash
# Clone the repository
git clone <repo-url>
cd ai-workspace

# Create your environment file
copy .env.example .env
# Edit .env and fill in all required values
```

### 3. Start Infrastructure (Development)

Start only the infrastructure services, run backend and frontend locally:

```bash
docker compose up -d postgres redis qdrant ollama langfuse prometheus grafana
```

### 4. Start Full Stack

```bash
docker compose up -d
```

### 5. Pull Default Ollama Models

```bash
# Chat model
docker exec ai-ollama ollama pull llama3.1:8b

# Coding model
docker exec ai-ollama ollama pull qwen2.5-coder:7b

# Embedding model (required for RAG)
docker exec ai-ollama ollama pull nomic-embed-text
```

## Service URLs

| Service    | URL                          | Purpose                    |
|------------|------------------------------|----------------------------|
| Backend    | http://localhost:8000        | FastAPI REST API           |
| API Docs   | http://localhost:8000/docs   | OpenAPI / Swagger UI       |
| Frontend   | http://localhost:5173        | React Web UI               |
| Langfuse   | http://localhost:3001        | LLM Tracing                |
| Prometheus | http://localhost:9090        | Metrics                    |
| Grafana    | http://localhost:3002        | Dashboards (admin/[pass])  |
| Qdrant     | http://localhost:6333        | Vector DB Dashboard        |

## Model Routing

| Task | Provider | Notes |
|------|----------|-------|
| Simple chat, Q&A, summaries | Local (Ollama) | Private, free, fast |
| Embeddings & indexing | Local (Ollama) | `nomic-embed-text` |
| Complex reasoning, long-context | Cloud (OpenRouter) | Requires API key |

Cloud provider is pluggable — change `CLOUD_PROVIDER` in `.env`.

## Hardware

Optimised for **NVIDIA RTX 3070 Ti** (8 GB VRAM):

- Max local model: 7B parameters at Q4/Q5 quantisation
- Embeddings run GPU-accelerated
- Reranking runs on CPU to free VRAM for inference

## Directory Structure

```
ai-workspace/
├── backend/               # FastAPI backend
├── frontend/              # React/Vite frontend
├── docker/
│   ├── postgres/init.sql  # DB initialisation
│   ├── prometheus/        # Prometheus config
│   └── grafana/           # Grafana provisioning
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Development

See [agent.md](agent.md) for coding standards, architecture rules, and workflow guidelines.

See [requirements.md](requirements.md) for full functional and non-functional requirements.
