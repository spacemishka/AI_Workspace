# User Manual — Personal AI Investment Analyst Platform

Welcome to the **Personal AI Investment Analyst** platform. This user manual explains how to start, configure, run financial analytics, and trigger multi-agent AI investment research using the platform.

---

## 1. Overview & Key Concepts

The platform is designed around three core principles:
1. **Privacy-First & Local-First**: Run LLMs locally via **Ollama** (e.g. `llama3.1:8b`) with zero data leaving your hardware. Optional cloud fallback via **OpenRouter** is available for complex research tasks when enabled.
2. **100% Deterministic Calculations**: Financial ratios (ROE, ROIC, FCF margins), Piotroski F-Score, Altman Z-Score, and DCF intrinsic valuation models are calculated via pure Python math algorithms to eliminate hallucinated numbers.
3. **Multi-Agent Orchestration**: A **Chief Investment Officer (CIO)** agent coordinates specialized sub-agents (*Fundamental Analyst*, *Financial Statement Analyst*, *Valuation Analyst*) to generate structured investment thesis reports.

---

## 2. Getting Started & Starting Services

### Step 1: Automated Setup
Run the setup wizard in PowerShell to verify prerequisites, configure secrets, pull Ollama models, and start the Docker container stack:

```powershell
.\setup.ps1
```

### Step 2: Everyday Service Management
Use the developer script to start, inspect, or stop background services:

```powershell
# Start all infrastructure and backend services
.\scripts\dev.ps1 start

# Check service health and Ollama VRAM usage
.\scripts\dev.ps1 status

# View live service logs
.\scripts\dev.ps1 logs

# Stop all background containers
.\scripts\dev.ps1 stop
```

### Service URL Directory

| Service | Access URL | Description |
| :--- | :--- | :--- |
| **Open WebUI** | [http://localhost:3080](http://localhost:3080) | Interactive chat web interface connected to Ollama |
| **FastAPI REST API** | [http://localhost:8000](http://localhost:8000) | Application backend |
| **Swagger API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API testing documentation |
| **Langfuse Observability** | [http://localhost:3001](http://localhost:3001) | LLM trace and prompt monitoring |
| **Grafana Metrics** | [http://localhost:3002](http://localhost:3002) | System & infrastructure performance dashboards |

---

## 3. Interactive Web Chat Interface (Open WebUI)

1. Open your browser and navigate to **[http://localhost:3080](http://localhost:3080)**.
2. On first launch, create your local admin account.
3. Select your desired local model from the dropdown (e.g., `llama3.1:8b` or `qwen2.5-coder:7b`).
4. Type investment or financial analysis prompts, such as:
   - *"Explain the difference between ROIC and ROE for a capital-intensive manufacturing business."*
   - *"What are the 9 criteria evaluated in the Piotroski F-Score?"*
   - *"What factors indicate a wide economic moat for a technology software company?"*

---

## 4. Using the REST API & Financial Analytics

The FastAPI backend exposes endpoints for deterministic financial analytics and multi-agent research. You can test these directly via the Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) or via `curl` / Python requests.

### Endpoint A: Deterministic Financial Analytics
Fetch company metadata, profitability margins, return metrics, financial distress scores, and DCF intrinsic valuation:

```http
GET /api/v1/financials/{ticker}/analysis
```

#### Query Parameters:
- `wacc` *(float, default: `0.09`)*: Weighted Average Cost of Capital discount rate (9%).
- `growth_rate` *(float, default: `0.10`)*: 5-year expected annual Free Cash Flow growth rate (10%).

> [!TIP]
> **Windows PowerShell Users**: In PowerShell, `curl` is aliased to `Invoke-WebRequest`. Use `curl.exe` or `Invoke-RestMethod` instead:
> ```powershell
> curl.exe "http://localhost:8000/api/v1/financials/AAPL/analysis?wacc=0.09&growth_rate=0.10"
> # or:
> Invoke-RestMethod "http://localhost:8000/api/v1/financials/AAPL/analysis"
> ```

#### Example Request (`cURL`):
```bash
curl.exe -X GET "http://localhost:8000/api/v1/financials/AAPL/analysis?wacc=0.09&growth_rate=0.10"
```

#### Example JSON Response:
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "market_cap": 3450000000000.0,
  "pe_ratio": 33.5,
  "ratios": {
    "gross_margin": 0.462,
    "operating_margin": 0.307,
    "net_margin": 0.253,
    "fcf_margin": 0.261,
    "roe": 1.52,
    "roa": 0.28,
    "roic": 0.54,
    "current_ratio": 0.87,
    "debt_to_equity": 1.41
  },
  "altman_z_score": 8.42,
  "altman_z_zone": "Safe",
  "dcf_intrinsic_value": 215.40
}
```

---

### Endpoint B: Multi-Agent Fundamental Research Workflow
Trigger the multi-agent research analysis on a company ticker. The **Chief Investment Officer (CIO)** agent coordinates sub-agents to analyze business models, moats, financial statements, and valuation margins of safety.

```http
POST /api/v1/analysis/company/{ticker}
```

#### Query Parameters:
- `cloud` *(boolean, default: `false`)*: Set to `true` to route reasoning tasks to cloud models (e.g., OpenRouter `claude-3.5-sonnet`) or `false` to keep execution 100% local via Ollama.

#### Example Request (`cURL`):
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/company/NVDA?cloud=false"
```

#### Example Response Structure:
```json
{
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "overall_rating": "Bullish",
  "conviction_score": 8.8,
  "executive_summary": "NVIDIA exhibits exceptional revenue growth driven by AI compute demand. Operating margins exceed 60% with a wide economic moat derived from CUDA ecosystem lock-in.",
  "investment_thesis": [
    "CUDA software platform creates high switching costs for enterprise AI developers.",
    "Data center GPU dominance provides strong pricing power and gross margins above 70%.",
    "Piotroski F-Score of 8 highlights pristine balance sheet strength and expanding ROIC."
  ],
  "key_risks": [
    "High customer concentration among hyper-scaler cloud providers.",
    "Geopolitical export regulations affecting hardware distribution."
  ],
  "fundamental_analysis": {
    "agent_name": "fundamental_analyst",
    "summary": "Wide moat backed by proprietary software stack and hardware leadership.",
    "findings": { "moat": "Wide", "moat_sources": ["Switching Costs", "Intangible Assets"] }
  },
  "financial_statement_analysis": {
    "agent_name": "financial_statement_analyst",
    "summary": "Pristine balance sheet with zero financial distress risk.",
    "findings": { "cash_flow_quality": "High", "accrual_risk": "Low" }
  },
  "valuation_analysis": {
    "agent_name": "valuation_analyst",
    "summary": "Trading at a premium multiple, requiring sustained >30% growth to justify DCF model.",
    "findings": { "margin_of_safety": "Moderate" }
  }
}
```

---

## 5. Interpreting Financial Scores

### Piotroski F-Score (0 to 9)
Evaluates 9 discrete criteria across Profitability, Leverage/Liquidity, and Operating Efficiency:
- **7 to 9**: **Strong Financial Health** (High quality balance sheet and improving operational efficiency).
- **4 to 6**: **Average Financial Stability**.
- **0 to 3**: **Weak / Distressed** (Potential liquidity or profitability red flags).

### Altman Z-Score
Predicts corporate insolvency likelihood for public non-financial companies:
- **Z > 2.99**: **Safe Zone** (Low risk of financial distress).
- **1.81 <= Z <= 2.99**: **Grey Zone** (Moderate financial distress risk).
- **Z < 1.81**: **Distress Zone** (High risk of insolvency).

### Beneish M-Score
Detects earnings manipulation probabilities based on 8 financial statement indices:
- **M > -1.78**: **High Probability of Earnings Manipulation** (Flagged for detailed accounting review).
- **M <= -1.78**: **Unlikely Manipulator** (Normal financial accounting).

---

## 6. Configuration & Environment Settings (`.env`)

You can customize model selections, API keys, and endpoints in the top-level `.env` file:

```ini
# -- Local Inference Settings ---------------------------------------------------
LOCAL_INFERENCE_BASE_URL=http://ollama:11434/v1
OLLAMA_DEFAULT_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=nomic-embed-text

# -- Cloud Provider (Optional Pluggable Integration) ---------------------------
CLOUD_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=moonshotai/kimi-k2.6
```

---

## 7. Troubleshooting & FAQ

#### Q: How do I change the default local model?
Run `.\scripts\dev.ps1 pull-models` or run `ollama pull <model-name>` in PowerShell, then select the model in Open WebUI.

#### Q: Where are database files and vector indices saved?
PostgreSQL data, Redis caches, and Qdrant vector collections are stored in persistent Docker named volumes managed automatically by `docker-compose.yml`.

#### Q: Is my data sent to any third-party APIs?
By default, **no**. All queries, statements, ratios, and multi-agent workflows execute locally using Ollama and local Python algorithms. Cloud routing is only invoked if you explicitly pass `cloud=true` on an API request.
