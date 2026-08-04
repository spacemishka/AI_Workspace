# Local AI Workspace - Requirements

## Vision

Build a privacy-first, local AI assistant that runs on consumer hardware and can securely access personal knowledge, documents, databases, and development tools.

The assistant should behave like a capable software engineer and research assistant while keeping all sensitive data local whenever possible.

---

# Goals

* Local-first architecture
* Modular and extensible
* LLM provider independent
* Support both local and cloud models
* Easy deployment using Docker
* Cross-platform (Windows first, Linux compatible)
* API-first architecture
* MCP compatible
* Multi-agent ready

---

# Hardware

## Development Machine

* GPU: NVIDIA RTX 3070 Ti (8 GB VRAM)
* Minimum RAM: 32 GB
* OS: Windows 11 (primary), Linux (Docker target)
* CUDA 12.x + cuDNN required for GPU-accelerated inference

## Local Inference Constraints

* Maximum model size: 7B parameters at Q4/Q5 quantisation for comfortable VRAM fit
* 13B models are borderline — use only with CPU offloading if needed
* Embeddings run GPU-accelerated via Ollama or SentenceTransformers
* Background indexing and reranking may run on CPU to keep VRAM free for inference

---

# Functional Requirements

## Chat

* Natural language conversations
* Conversation history
* Streaming responses
* Multiple model selection
* Session management

---

## Model Routing

The system applies a **local-first** routing strategy:

| Task Complexity | Routing | Rationale |
|---|---|---|
| Simple (chat, Q&A, short summaries, embeddings) | Local (Ollama, RTX 3070 Ti) | Privacy, speed, zero cost |
| Complex (long-context reasoning, code generation, multi-step agents) | Cloud provider | Exceeds local VRAM or latency budget |

Routing rules:

* Default to local whenever the task fits within the performance budget.
* Route to cloud only when the local model is insufficient for the task.
* Never send personal or sensitive data to cloud providers without explicit user consent.
* Cloud provider is **pluggable** — switching provider requires only a config change.

Current cloud provider:

* **OpenRouter** — aggregates multiple cloud LLMs via a single OpenAI-compatible API endpoint.

Future cloud providers (pluggable):

* Anthropic (Claude)
* Google (Gemini)
* Mistral AI
* Any OpenAI-compatible endpoint

The router must:

* Expose a unified provider interface regardless of backend.
* Log which provider handled each request (for cost and audit tracking).
* Support per-user and per-agent provider overrides via configuration.
* Fall back gracefully to local if cloud is unreachable.

---

## Knowledge Base

Support indexing and searching:

* PDF
* Markdown
* Word documents
* Text files
* HTML
* CSV
* JSON

Features:

* Incremental indexing
* Metadata extraction
* Semantic search
* Hybrid search
* Source citation

---

## Retrieval (RAG)

* Embedding generation
* Vector database integration
* Context compression
* Query rewriting
* Document ranking
* Configurable chunking strategy

---

## Database Access

Read-only support for:

* PostgreSQL
* SQL Server
* SQLite

Capabilities:

* Natural language to SQL
* SQL validation
* Result explanation
* Chart-ready output

---

## Development Assistant

Support:

* Git repositories
* Code search
* Code explanation
* Refactoring suggestions
* Documentation generation
* Unit test generation

Languages:

* Python
* Apex
* JavaScript
* TypeScript
* SQL
* C#

---

## Tool Calling

Support tools through MCP:

Examples:

* File system
* Git
* SQL
* REST APIs
* Weather
* Calendar
* Email
* Browser automation

---

## Agent System

Support specialized agents.

Examples:

* Coding Agent
* Research Agent
* Database Agent
* Documentation Agent
* Planning Agent

Future:

* Multi-agent collaboration

---

## Memory

* Conversation memory
* Project memory
* User preferences
* Long-term memory
* Searchable memories

Implementation:

* Short-term: conversation context stored in PostgreSQL
* Long-term: vector search over memory entries using Qdrant
* Technology: **mem0** (default) or custom PostgreSQL + Qdrant store
* Memory entries must be attributable (timestamped, source-tagged)

---

## Local Models

Local inference runtime:

* **Ollama** — primary local runtime (GPU-accelerated, fits 3070 Ti)
* **LM Studio** — optional GUI-based alternative
* **vLLM** — remote/cloud deployment only (requires ≥ 16 GB VRAM)

Default chat models (Q4 quantised):

* `qwen2.5-coder:7b` — coding tasks
* `llama3.1:8b` — general chat
* `mistral:7b` — fast reasoning
* `gemma2:9b` — balanced quality
* `deepseek-coder-v2:16b` — advanced coding (CPU offload)

Embedding models:

* **`nomic-embed-text`** — default, runs via Ollama (274M, GPU)
* **`mxbai-embed-large`** — higher quality alternative (335M, GPU)
* Library: `sentence-transformers` for Python-side embedding

Reranking:

* `cross-encoder/ms-marco-MiniLM-L-6-v2` — CPU-based reranker

Cloud providers should be pluggable via provider abstraction.

---

## Security

Authentication:

* **JWT tokens** for session-based API access
* **API keys** for programmatic / agent access
* Token storage: HTTP-only cookies (web) or bearer headers (API clients)
* No external auth provider required in initial version

Authorisation:

* Role-based permissions (admin, user, readonly)
* Per-agent and per-tool permission scopes

Secrets management:

* All secrets via environment variables (`.env` file, never committed)
* Docker secrets for production
* No hardcoded credentials anywhere

Other:

* Audit logs for all LLM calls, tool executions, and data access
* Encrypted configuration for sensitive YAML values
* All user input validated with Pydantic before processing

---

## Observability

Logging:

* **structlog** — structured JSON logging throughout the backend
* Log level configurable per module via YAML
* All LLM calls logged with model, token count, and latency

Tracing:

* **Langfuse** — local LLM call tracing, prompt management, and cost tracking
* Trace every agent step, tool call, and RAG retrieval

Metrics:

* **Prometheus** — expose `/metrics` endpoint from FastAPI
* **Grafana** — dashboards for inference latency, queue depth, indexing progress
* Alert on hard-limit budget breaches (see agent.md Performance Budgets)

---

## User Interface

Web interface:

* Chat
* Document browser
* Agent management
* Model management
* Settings
* Search

Optional desktop application later.

---

# Non-Functional Requirements

* Modular architecture
* High test coverage
* Strong typing
* Structured logging
* Configuration via YAML
* Plugin architecture
* Docker support
* REST API
* OpenAPI documentation

---

# Future Features

* Voice interface
* Image understanding
* OCR
* Local speech-to-text
* Text-to-speech
* Home Assistant integration
* Email automation
* Workflow automation
* Mobile companion app

---

# Initial Technology Stack

## Backend

* **Python 3.12+**
* **FastAPI** — REST API + OpenAPI documentation
* **SQLAlchemy** — ORM for internal PostgreSQL access
* **Alembic** — database migrations
* **Pydantic v2** — data validation and settings management
* **ARQ** — async task queue (Redis-backed) for indexing and embedding jobs
* **structlog** — structured JSON logging

## AI / LLM

* **Ollama** — local model inference (primary)
* **LangChain** — LLM orchestration, agent framework, RAG pipelines
* **sentence-transformers** — local embedding generation
* **OpenRouter** — current cloud provider (OpenAI-compatible, pluggable)
* **Langfuse** — LLM call tracing and observability (tracks local vs cloud routing decisions)

## Vector & Data Store

* **PostgreSQL** — relational store (conversations, users, memory, metadata)
* **Qdrant** — vector database (dense + sparse for hybrid search)
* **Redis** — task queue backend (ARQ) and short-term cache

## Frontend

* **React 18+**
* **TypeScript**
* **Vite** — build tool and dev server
* **Zustand** — lightweight state management
* **React Query (TanStack Query)** — server state, caching, streaming
* **SSE / WebSocket** — streaming response handling

## Deployment

* **Docker**
* **Docker Compose** — local multi-service orchestration
* `.env.example` — documented environment variable template

## Observability

* **Prometheus** — metrics collection
* **Grafana** — dashboards
* **Langfuse** — LLM tracing (self-hosted via Docker)

## Developer Tooling

* **Pytest** — unit and integration testing
* **pytest-cov** — test coverage reporting (target: ≥ 80%)
* **Ruff** — linting
* **Black** — code formatting
* **mypy** — static type checking
* **pre-commit** — enforce lint, format, and type checks on every commit

---

# Success Criteria

The first production-ready version should allow a user to:

1. Chat with local and cloud LLMs.
2. Search personal documents using RAG.
3. Query SQL databases using natural language.
4. Analyze Git repositories.
5. Execute tools through MCP.
6. Use specialized AI agents.
7. Keep all personal data under user control.
