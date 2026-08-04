# Local AI Workspace – Gap Analysis

> Based on [requirements.md](file:///c:/Users/peter/AI_Dev/AI_Workspace/requirements.md) and [agent.md](file:///c:/Users/peter/AI_Dev/AI_Workspace/agent.md)  
> Hardware context: **NVIDIA RTX 3070 Ti** (8 GB VRAM) — suitable for local embedding models & small/medium LLMs.

---

## 1. Hardware & GPU Constraints — Missing Entirely

The requirements make no mention of hardware at all. Given the 3070 Ti (8 GB VRAM), this matters significantly.

| Gap | Recommendation |
|---|---|
| No GPU / VRAM budget defined | Add a hardware profile section (min / recommended specs) |
| No model size constraints | Only models ≤ 7B (Q4/Q5 quant) fit comfortably; 13B is borderline |
| No CUDA / ROCm requirement stated | Specify CUDA 12.x + cuDNN for Ollama/vLLM GPU offloading |
| vLLM listed as a target, but vLLM needs ~16 GB+ for most use cases | Either remove vLLM or scope it to cloud/remote only |
| No embedding model selection guidance | Small embedding models (e.g., `nomic-embed-text`, `mxbai-embed-large`) are 3070 Ti friendly |

---

## 2. Technology Stack — Missing Components

### Backend / Runtime
| Missing | Why It Matters |
|---|---|
| **LangChain / LlamaIndex** (or similar orchestration) | RAG, agent orchestration, tool calling all need an LLM framework layer |
| **Celery + Redis** or **ARQ** | Async task queue for indexing, embedding jobs, background agents |
| **Alembic** | DB migrations for PostgreSQL (FastAPI projects always need this) |
| **Pydantic Settings** | Config management from YAML/env — agent.md says YAML config but no tooling listed |
| **SQLAlchemy** | ORM for internal DB access (not just user-facing SQL agent) |

### AI / Embeddings
| Missing | Why It Matters |
|---|---|
| **Embedding model** (local) | Requirements mention embedding generation but name no model. For 3070 Ti: `nomic-embed-text`, `all-MiniLM`, `mxbai-embed-large` |
| **Reranker model** | Needed for hybrid search / document ranking (e.g., `cross-encoder/ms-marco`) |
| **Sentence Transformers** | Python library to run embeddings locally |

### Vector DB
| Missing | Why It Matters |
|---|---|
| Qdrant is listed — ✅ | But no mention of **collection schema**, **distance metric**, or **sparse vector** support for hybrid search |
| No BM25 / keyword index | Hybrid search requires both dense vectors AND a BM25/keyword index (Qdrant supports this natively) |

### Frontend
| Missing | Why It Matters |
|---|---|
| No UI component library specified | React + TS but no Shadcn/UI, MUI, or similar — leaves a big implementation gap |
| No state management | Zustand / Redux / React Query not mentioned |
| No build tool | Vite or Next.js not chosen |
| No WebSocket / SSE handling | Streaming responses require SSE or WebSocket client |

### Observability
| Missing | Why It Matters |
|---|---|
| **Logging stack** | Structured logging mentioned but no tool (e.g., `structlog`, Loguru, OpenTelemetry) |
| **Tracing** | LLM calls need tracing (Langfuse, Phoenix Arize, or OpenTelemetry) |
| **Metrics** | No Prometheus / Grafana or similar |

### Developer Tooling
| Missing | Why It Matters |
|---|---|
| **Pre-commit hooks** | agent.md requires Ruff + Black but no enforcement mechanism defined |
| **CI pipeline** | No GitHub Actions / CI specified |
| **Environment management** | No `.env` / secrets management tooling (dotenv, Vault, etc.) |
| **Code coverage tool** | `pytest` listed but no `pytest-cov` / coverage threshold |

---

## 3. Functional Gaps

### Authentication & Auth Flow
- "Local authentication" is listed but **no mechanism** is specified.
  - Missing: JWT, API key strategy, session store (Redis?), OAuth2 for cloud provider tokens.

### MCP Integration
- requirements.md lists MCP as a goal but **no MCP server runtime** or SDK is named.
  - Missing: `mcp` Python SDK, how agents register/discover MCP servers, MCP tool manifest format.

### Memory / Long-term Storage
- Memory requirements are listed but **no technology** is named.
  - Missing: mem0, Zep, or a custom PostgreSQL-backed memory store.
  - No graph memory option (e.g., MemGraph / Neo4j) despite agent system requiring complex relationships.

### Multi-agent Coordination
- Listed as "Future" but agent.md's Long-Term Goal makes it core.
  - Missing: Agent communication protocol (e.g., A2A), task routing, agent registry.

### Data Ingestion Pipeline
- Knowledge Base lists formats (PDF, Markdown, etc.) but no ingestion pipeline design.
  - Missing: file watcher / scheduler, de-duplication strategy, ingestion status tracking.

### Monitoring & Rate Limiting
- No mention of rate limiting for API endpoints or LLM calls (critical for local hardware resource management on a 3070 Ti).

---

## 4. agent.md — Quality Assessment

The [agent.md](file:///c:/Users/peter/AI_Dev/AI_Workspace/agent.md) is well-structured and aligned with the requirements. However it is missing:

| Gap | Recommendation |
|---|---|
| No markdown formatting (headers use plain text) | Add `#` headings for readability in IDEs / Antigravity |
| No project structure conventions | Define folder layout (`src/`, `tests/`, `docs/`, `docker/`) |
| No branching / PR strategy | Define `main` + feature branches, PR checklist |
| No versioning strategy | SemVer or CalVer? |
| No performance budget | Latency targets for RAG queries, streaming TTFT (Time To First Token) |
| No definition of "done" per feature | agent.md says "Never consider a feature complete without tests" but no acceptance criteria template |

---

## 5. RTX 3070 Ti – Recommended Model Configuration

Given 8 GB VRAM:

| Use Case | Recommended Model | Tool |
|---|---|---|
| General chat / coding | `qwen2.5-coder:7b-q4` or `llama3.1:8b-q4` | Ollama |
| Embeddings | `nomic-embed-text` (274M) | Ollama / SentenceTransformers |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` | SentenceTransformers (CPU) |
| Vision (future) | `llava:7b-q4` | Ollama |
| Speech-to-text (future) | `whisper:base` or `small` | faster-whisper (CPU) |

> [!CAUTION]
> vLLM requires significantly more VRAM than Ollama for the same model. On a 3070 Ti, **Ollama is the practical choice** for local inference. Consider removing vLLM from initial scope or limiting it to remote/cloud deployment only.

---

## 6. Priority Recommendations

### Must-add to `requirements.md`
1. **Hardware profile section** — min specs, VRAM budget, CUDA version
2. **Embedding model selection** — name a specific default model
3. **Auth mechanism** — specify JWT or API key approach
4. **Async task queue** — Celery/Redis or ARQ for indexing jobs
5. **Memory technology** — choose mem0, Zep, or custom PostgreSQL store
6. **Observability stack** — logging (structlog), tracing (Langfuse), metrics
7. **Frontend build tool** — Vite or Next.js
8. **Remove vLLM from initial scope** or explicitly scope it to remote only

### Must-add to `agent.md`
1. **Markdown formatting** — add proper `#` headers
2. **Project folder conventions** — define the repo layout
3. **Branching & PR strategy**
4. **Performance budgets** — latency targets per feature
5. **Feature acceptance criteria template**
