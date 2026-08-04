# AI Workspace — Setup Guide

> **Hardware assumed:** NVIDIA RTX 3070 Ti · Windows 11 · 32 GB RAM

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Initial Project Setup](#2-initial-project-setup)
3. [Option A — Ollama (Recommended)](#3-option-a--ollama-recommended)
4. [Option B — llama.cpp Server](#4-option-b--llamacpp-server)
5. [Option C — LM Studio](#5-option-c--lm-studio)
6. [Post-Setup Configuration](#6-post-setup-configuration)
7. [Verification Checklist](#7-verification-checklist)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### 1.1 Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA RTX 3060 (8 GB) | RTX 3070 Ti (8 GB) |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB free | 100 GB free (models are large) |

### 1.2 Software

| Software | Version | Download |
|----------|---------|----------|
| Windows 11 | 22H2+ | — |
| Docker Desktop | 4.30+ | https://www.docker.com/products/docker-desktop |
| Git | Latest | https://git-scm.com |
| Python | 3.12+ | https://www.python.org |
| Node.js | 20 LTS | https://nodejs.org |

### 1.3 Docker Desktop — WSL2 Backend (Required)

> GPU passthrough requires the WSL2 backend. Without it, Ollama and llama.cpp cannot use the RTX 3070 Ti.

1. Open **Docker Desktop → Settings → General**
2. Ensure **"Use WSL 2 based engine"** is checked ✅
3. Go to **Settings → Resources → WSL Integration**
4. Enable integration for your default WSL2 distro ✅
5. Click **Apply & Restart**

### 1.4 NVIDIA Container Toolkit (Required for GPU)

**Step 1 — Verify driver is installed (PowerShell):**
```powershell
nvidia-smi
```
You should see your RTX 3070 Ti. If not, install the latest driver from https://www.nvidia.com/drivers.

**Step 2 — Install NVIDIA Container Toolkit inside WSL2:**

Open a WSL2 terminal (search "Ubuntu" in Start menu):
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Step 3 — Verify GPU is accessible in Docker (PowerShell):**
```powershell
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```
You should see the RTX 3070 Ti in the output.

---

## 2. Initial Project Setup

### 2.1 Clone and Configure

```powershell
git clone <repo-url>
cd ai-workspace
copy .env.example .env
```

### 2.2 Generate Required Secrets

```powershell
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('LANGFUSE_NEXTAUTH_SECRET=' + secrets.token_hex(32))"
python -c "import secrets; print('LANGFUSE_SALT=' + secrets.token_hex(16))"
```

Paste the output into your `.env`. Also set strong values for:
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `GRAFANA_ADMIN_PASSWORD`

### 2.3 Common .env Settings (all backends)

```env
ENVIRONMENT=development
POSTGRES_USER=aiworkspace
POSTGRES_PASSWORD=your_strong_password
POSTGRES_DB=aiworkspace
REDIS_PASSWORD=your_redis_password
CLOUD_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...your-key
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3.5-sonnet
```

Now choose **one** of the three inference backends below.

---

## 3. Option A — Ollama (Recommended)

> Easiest setup. Multi-model support. GPU-accelerated. Runs in Docker.

### 3.1 Configure .env

```env
LOCAL_INFERENCE_BASE_URL=http://ollama:11434/v1
OLLAMA_DEFAULT_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### 3.2 Start the Stack

```powershell
docker compose up -d postgres redis qdrant ollama langfuse prometheus grafana
```

Tail Ollama logs until it shows `Listening on [::]:11434`:
```powershell
docker compose logs -f ollama
```

### 3.3 Pull Models

```powershell
# REQUIRED — embedding model for RAG
docker exec ai-ollama ollama pull nomic-embed-text

# General chat (~4.7 GB, ~5 GB VRAM)
docker exec ai-ollama ollama pull llama3.1:8b

# Coding tasks (~4.7 GB, ~5 GB VRAM)
docker exec ai-ollama ollama pull qwen2.5-coder:7b

# Fast reasoning (~4.1 GB, ~4.5 GB VRAM)
docker exec ai-ollama ollama pull mistral:7b
```

> **VRAM note:** Only one 7B model fits in VRAM at a time on the RTX 3070 Ti.
> Ollama unloads/reloads automatically. If you get OOM errors, set
> `OLLAMA_MAX_LOADED_MODELS=1` in `.env`.

### 3.4 Verify Ollama

```powershell
# List downloaded models
curl http://localhost:11434/api/tags

# Test inference
curl http://localhost:11434/api/generate `
  -d "{\"model\": \"llama3.1:8b\", \"prompt\": \"Hello!\", \"stream\": false}"

# Check VRAM usage
docker exec ai-ollama ollama ps
```

### 3.5 Useful Ollama Commands

```powershell
# List loaded models and memory usage
docker exec ai-ollama ollama ps

# Remove a model to free disk space
docker exec ai-ollama ollama rm mistral:7b

# List all downloaded models
docker exec ai-ollama ollama list
```

---

## 4. Option B — llama.cpp Server

> Maximum control over a single model. Minimal overhead. You manage GGUF files manually.

### 4.1 Download a GGUF Model

Create a `models/` folder in the project root:
```powershell
mkdir models
```

Download from Hugging Face. Choose **Q4_K_M** quantisation for the best quality/VRAM balance on 8 GB.

Recommended models for RTX 3070 Ti:

| Model | File | Download Size | VRAM Required |
|-------|------|---------------|---------------|
| Llama 3.1 8B | `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` | 4.7 GB | ~5 GB |
| Qwen 2.5 Coder 7B | `Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf` | 4.7 GB | ~5 GB |
| Mistral 7B | `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` | 4.1 GB | ~4.5 GB |

Place the downloaded `.gguf` file in the `./models/` directory.

### 4.2 Fix the llamacpp Service in docker-compose.yml

Locate the `llamacpp` service and replace the `command` block with proper YAML list syntax:

```yaml
  llamacpp:
    image: ghcr.io/ggerganov/llama.cpp:server-cuda
    container_name: ai-llamacpp
    restart: unless-stopped
    volumes:
      - ./models:/models
    command:
      - --model
      - /models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
      - --host
      - "0.0.0.0"
      - --port
      - "8080"
      - --n-gpu-layers
      - "33"
      - --ctx-size
      - "8192"
      - --parallel
      - "2"
    ports:
      - "8080:8080"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - ai-network
```

> **`--n-gpu-layers 33`** offloads all layers of a 7B model to the RTX 3070 Ti.
> Reduce to `20` if you get out-of-memory errors.

### 4.3 Configure .env

```env
# Comment out other options
# LOCAL_INFERENCE_BASE_URL=http://ollama:11434/v1
LOCAL_INFERENCE_BASE_URL=http://llamacpp:8080/v1
```

Stop Ollama to free VRAM for llama.cpp:
```powershell
docker compose stop ollama
```

### 4.4 Start the Stack

```powershell
docker compose up -d postgres redis qdrant llamacpp langfuse prometheus grafana
```

### 4.5 Verify llama.cpp

```powershell
# Health check
curl http://localhost:8080/health

# List models
curl http://localhost:8080/v1/models

# Test inference (OpenAI-compatible)
curl http://localhost:8080/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d "{\"model\": \"local\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}"
```

### 4.6 Embeddings with llama.cpp

llama.cpp server handles one model at a time, so it cannot serve both a chat model and an
embedding model simultaneously. Options:

- **Keep Ollama running alongside** for embeddings only:
  ```powershell
  docker compose up -d ollama
  docker exec ai-ollama ollama pull nomic-embed-text
  ```
  Then set `OLLAMA_EMBED_MODEL=nomic-embed-text` and handle the two URLs in backend config.

- **Use a separate llama.cpp instance** on a different port with an embedding GGUF
  (e.g., `nomic-embed-text-v1.5.Q8_0.gguf`).

---

## 5. Option C — LM Studio

> GUI-based model management. Runs natively on Windows — **not** in Docker.
> Perfect if you prefer a visual interface for downloading and switching models.

### 5.1 Install LM Studio

1. Download from https://lmstudio.ai
2. Run the installer and launch LM Studio

### 5.2 Download Models in LM Studio

1. Click the **Search** tab (magnifying glass icon, left sidebar)
2. Search for a model, e.g. `llama-3.1-8b-instruct`
3. Select a GGUF variant:
   - **Q4_K_M** — recommended for RTX 3070 Ti (best quality within 8 GB VRAM)
4. Click **Download** (≈ 4.7 GB)
5. Also download an embedding model:
   - Search `nomic-embed-text-v1.5` and download `Q8_0` variant

### 5.3 Enable the Local Server

1. Click the **Local Server** tab (plug icon, left sidebar)
2. Select your downloaded model from the dropdown
3. Configure settings:
   - **Port:** `1234` (keep default)
   - **Enable CORS:** ✅ (required for Docker containers to reach the server)
   - **GPU Layers:** drag to maximum (33 for 7B models)
4. Click **Start Server**
5. Confirm you see: `LM Studio Server listening on port 1234`

> LM Studio must remain open and the server must be running whenever you use the backend.

### 5.4 Configure .env

```env
# Comment out other options
# LOCAL_INFERENCE_BASE_URL=http://ollama:11434/v1
# LOCAL_INFERENCE_BASE_URL=http://llamacpp:8080/v1
LOCAL_INFERENCE_BASE_URL=http://host.docker.internal:1234/v1
```

> **`host.docker.internal`** is a special Docker DNS hostname that resolves to your
> Windows host from inside any container. This is how the backend service (running in
> Docker) reaches LM Studio (running natively on Windows).

### 5.5 Start Infrastructure (without Ollama)

```powershell
# LM Studio handles inference — no Ollama or llamacpp needed
docker compose up -d postgres redis qdrant langfuse prometheus grafana
```

### 5.6 Verify LM Studio Connectivity

```powershell
# From your Windows host
curl http://localhost:1234/v1/models

# Simulate how the Docker backend reaches LM Studio
docker run --rm curlimages/curl http://host.docker.internal:1234/v1/models
```

Both should return a JSON response with the loaded model.

### 5.7 LM Studio Notes

- **Must be running before starting the backend.** The backend health check will fail if
  `LOCAL_INFERENCE_BASE_URL` is unreachable on startup.
- **Switching models:** select a different model in the Local Server tab and restart
  the server. Restart the backend container to pick up the change.
- **Embeddings:** LM Studio can serve embedding models too. Load `nomic-embed-text` via
  the Local Server and set a separate embed URL in backend config.
- **CORS must be enabled** — without it, the browser-based frontend cannot call the API.

---

## 6. Post-Setup Configuration

### 6.1 Langfuse — First Login

1. Open http://localhost:3001
2. Click **Sign Up** and create your admin account
3. Go to **Settings → API Keys**
4. Click **Create API Key** — copy both the **Public Key** and **Secret Key**
5. Add to `.env`:
   ```env
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   ```
6. Restart the backend:
   ```powershell
   docker compose restart backend worker
   ```

### 6.2 Grafana — First Login

1. Open http://localhost:3002
2. Login: `admin` / `your GRAFANA_ADMIN_PASSWORD`
3. Prometheus is already pre-configured as a datasource (auto-provisioned)
4. Import dashboards:
   - **Dashboards → Import → ID `1860`** — Node Exporter (system metrics)

### 6.3 Run Database Migrations

```powershell
docker compose run --rm backend alembic upgrade head
```

### 6.4 Start Application Services

```powershell
docker compose up -d backend worker frontend
```

---

## 7. Verification Checklist

```powershell
# ── Infrastructure ────────────────────────────────────────────────────────────

# PostgreSQL
docker exec ai-postgres pg_isready -U aiworkspace
# Expected: /var/run/postgresql:5432 - accepting connections

# Redis
docker exec ai-redis redis-cli -a $env:REDIS_PASSWORD ping
# Expected: PONG

# Qdrant
curl http://localhost:6333/healthz
# Expected: {"title":"qdrant - vector search engine",...}

# ── Inference Backend ─────────────────────────────────────────────────────────

# Ollama
curl http://localhost:11434/api/tags

# llama.cpp
curl http://localhost:8080/health

# LM Studio (from host)
curl http://localhost:1234/v1/models

# ── Application ───────────────────────────────────────────────────────────────

# Backend health
curl http://localhost:8000/health

# ── Browser Checks ────────────────────────────────────────────────────────────

start http://localhost:8000/docs   # API docs
start http://localhost:5173        # Frontend
start http://localhost:3001        # Langfuse
start http://localhost:3002        # Grafana

# ── GPU Verification ──────────────────────────────────────────────────────────
nvidia-smi
docker exec ai-ollama ollama ps    # Ollama only
```

---

## 8. Troubleshooting

### GPU not detected in Docker

**Error:** `could not select device driver "" with capabilities: [[gpu]]`

```bash
# In WSL2
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
Then restart Docker Desktop from the system tray.

---

### Ollama out of memory (OOM)

**Error:** `model requires more system memory than is available`

- Set `OLLAMA_MAX_LOADED_MODELS=1` and `OLLAMA_NUM_PARALLEL=1` in `.env`
- Try a Q3_K_M quantised model (~3.5 GB VRAM)
- Run `docker exec ai-ollama ollama ps` to see what's currently loaded

---

### LM Studio unreachable from Docker

**Error:** `Connection refused: host.docker.internal:1234`

1. Is LM Studio server started? Check the Local Server tab shows "listening on 1234".
2. Is CORS enabled in LM Studio Local Server settings?
3. Add `extra_hosts` to the `backend` service in `docker-compose.yml`:
   ```yaml
   extra_hosts:
     - "host.docker.internal:host-gateway"
   ```

---

### Langfuse database error on startup

**Error:** `relation "traces" does not exist`

```powershell
docker exec ai-postgres psql -U aiworkspace -c "CREATE DATABASE langfuse;"
docker compose restart langfuse
```

---

### Backend cannot connect to Postgres

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

Wait for Postgres to be fully healthy before starting the backend:
```powershell
docker compose up -d postgres
docker compose ps postgres    # wait until status shows "healthy"
docker compose up -d backend
```

---

### Redis authentication failed

**Error:** `WRONGPASS invalid username-password pair`

If you changed `REDIS_PASSWORD` after the volume was created, destroy and recreate:
```powershell
docker compose down
docker volume rm ai-workspace-redis
docker compose up -d redis
```

---

## Service Port Reference

| Service | URL | Notes |
|---------|-----|-------|
| Backend API | http://localhost:8000 | FastAPI |
| API Docs | http://localhost:8000/docs | OpenAPI / Swagger |
| Frontend | http://localhost:5173 | React / Vite |
| Langfuse | http://localhost:3001 | LLM Tracing |
| Grafana | http://localhost:3002 | Dashboards |
| Prometheus | http://localhost:9090 | Metrics |
| Qdrant Dashboard | http://localhost:6333/dashboard | Vector DB |
| Ollama API | http://localhost:11434 | Option A |
| llama.cpp API | http://localhost:8080 | Option B |
| LM Studio API | http://localhost:1234 | Option C |
