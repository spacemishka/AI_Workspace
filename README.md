# AI Workspace

Privacy-first, local AI assistant running on consumer hardware.

## Quick Start

### Automated Setup (Recommended)

Run the interactive setup wizard — it handles everything:

```powershell
git clone <repo-url>
cd ai-workspace
.\setup.ps1
```

The wizard will:
- ✅ Check all prerequisites (Docker, GPU, Python)
- ✅ Ask you to choose an inference backend (Ollama / llama.cpp / LM Studio)
- ✅ Generate secrets and create your `.env`
- ✅ Start the Docker stack
- ✅ Pull Ollama models
- ✅ Verify all services are healthy

### Manual Setup

See [docs/setup-guide.md](docs/setup-guide.md) for step-by-step instructions for each backend.

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
