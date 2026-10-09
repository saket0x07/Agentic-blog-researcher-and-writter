# 🤖 Agentic Blog Researcher & Writer

> **Automated, research-backed technical blog generation powered by LangGraph, LLMs, and Multi-Modal AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker Image](https://img.shields.io/badge/Docker-saket0x07%2Fblog--agent-2496ed.svg)](https://hub.docker.com/r/saket0x07/blog-agent)
[![Interactive Flow Map](https://img.shields.io/badge/Archify-Interactive_Flow_Diagram-6366f1.svg)](#-interactive-architecture--workflow-map)

---

## 🗺️ Interactive Architecture & Workflow Map

This project includes an **interactive system architecture and workflow visualizer** built using [Archify](https://github.com/tt-a1i/archify) design standards.

### 🌟 Try the Standalone Interactive Visual
You can open and explore the full interactive SVG dashboard directly in your browser:

👉 **[Open Interactive Architecture Diagram (`docs/interactive_flow.html`)](docs/interactive_flow.html)**

**Features of the Interactive Diagram:**
- 🔍 **Click-to-Inspect**: Click any node to open the inspector showing exact source files, input/output states, and code snippets.
- 🎬 **Flow Simulator**: Click **"▶ Run Flow Simulator"** to watch animated data pulses step through the 2-phase LangGraph lifecycle.
- 🌓 **Theme Switcher**: Instant Dark Mode and Light Mode switching.
- 🔎 **Lenses & Filters**: Toggle views between *All Subsystems*, *LangGraph Core*, *Worker Fan-Out*, and *Clients & Deploy*.
- 📐 **Pan & Zoom**: Smooth mouse wheel zooming and canvas dragging.
- 💾 **Export**: One-click SVG vector export.

> **Quick command to launch the diagram locally in your browser:**
> ```powershell
> Start-Process docs/interactive_flow.html
> ```

---

## 📊 End-to-End System Workflow

Below is the live GitHub-rendered workflow diagram demonstrating the complete implementation:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#1e293b', 'primaryTextColor': '#f8fafc', 'primaryBorderColor': '#6366f1', 'lineColor': '#38bdf8', 'secondaryColor': '#0f172a', 'tertiaryColor': '#1e293b'}}}%%
flowchart TD
    subgraph S1["1. Client & Delivery Layer"]
        UI["🖥️ Streamlit Web App<br/>(app.py : Port 8501)"]
        API["⚡ FastAPI REST API<br/>(api.py : Port 8000)"]
        DOCKER["🐳 Docker Container<br/>(AWS EC2 t2.micro + 2GB Swap)"]
    end

    subgraph S2["2. Phase 1: Planning & Dynamic Research"]
        STATE["📦 OverallState Initializer<br/>(blog_agent/graph/state.py)"]
        ROUTER{"🧭 Smart Router Node<br/>(nodes/router.py)<br/>closed_book | open_book | hybrid"}
        RESEARCH["🔍 Dynamic Research Node<br/>(nodes/research.py)<br/>Generates 3-10 Search Queries"]
        TAVILY[("🌐 Tavily Search Engine<br/>utils/tavily_client.py<br/>(w/ Mock Search Fallback)")]
        PLANNER["📋 Structured Planner Node<br/>(nodes/planner.py)<br/>Outputs Pydantic PlanObject"]
    end

    subgraph S3["3. Phase 2: Parallel Content Execution"]
        FANOUT{"⚡ Dynamic Map-Reduce Fan-Out<br/>(LangGraph Send API)"}
        W1["✍️ Worker 1: Intro & Context<br/>(nodes/worker.py)"]
        W2["✍️ Worker 2: Core Architecture<br/>(nodes/worker.py)"]
        W3["✍️ Worker 3: Implementation Code<br/>(nodes/worker.py)"]
        W4["✍️ Worker 4: Best Practices & Outlook<br/>(nodes/worker.py)"]
        TRACKER["💰 TokenUsageCallbackHandler<br/>Tracks prompt, completion tokens & USD cost"]
    end

    subgraph S4["4. Synthesis, Multimodal Generation & Storage"]
        REDUCER["🧩 Multimodal Reducer Node<br/>(nodes/reducer.py)<br/>Stitches Drafts & Plans Images"]
        IMAGES[("🎨 Multimodal Image Generator<br/>Gemini Imagen 3 | FLUX | Pillow Fallback")]
        MARKDOWN["📄 Output Blog Artifact<br/>(output/topic_name.md)"]
    end

    %% Client Interactions
    UI -->|Topic Input| STATE
    API -->|POST /blog/write| STATE
    DOCKER -.->|Hosts| UI
    DOCKER -.->|Hosts| API

    %% Phase 1 Connections
    STATE --> ROUTER
    ROUTER -->|"open_book / hybrid"| RESEARCH
    ROUTER -->|"closed_book (skip search)"| PLANNER
    RESEARCH <-->|HTTP / Mock| TAVILY
    RESEARCH -->|Evidence Pack| PLANNER

    %% Phase 2 Connections
    PLANNER -->|tasks: List[TaskObject]| FANOUT
    FANOUT -->|Send()| W1
    FANOUT -->|Send()| W2
    FANOUT -->|Send()| W3
    FANOUT -->|Send()| W4
    W1 -.->|Metrics| TRACKER
    W2 -.->|Metrics| TRACKER
    W3 -.->|Metrics| TRACKER
    W4 -.->|Metrics| TRACKER

    %% Phase 3 Connections
    W1 -->|section_drafts| REDUCER
    W2 -->|section_drafts| REDUCER
    W3 -->|section_drafts| REDUCER
    W4 -->|section_drafts| REDUCER
    REDUCER -->|ImagePlan (max 3)| IMAGES
    IMAGES -->|Saved PNGs| REDUCER
    REDUCER -->|Compiled Markdown| MARKDOWN

    %% Styling
    classDef client fill:#0f172a,stroke:#34d399,stroke-width:2px;
    classDef router fill:#1e293b,stroke:#fbbf24,stroke-width:2px;
    classDef node fill:#1e293b,stroke:#38bdf8,stroke-width:2px;
    classDef worker fill:#1e293b,stroke:#c084fc,stroke-width:2px;
    classDef output fill:#0f172a,stroke:#34d399,stroke-width:2px;
    
    class UI,API,DOCKER client;
    class ROUTER router;
    class RESEARCH,PLANNER,REDUCER node;
    class W1,W2,W3,W4,FANOUT worker;
    class MARKDOWN output;
```

---

## 🎯 Key Capabilities & Highlights

1. **Two-Phase Agentic Execution**:
   - **Phase 1: Planning**: Evaluates topic needs, queries external sources dynamically, and builds an exhaustive outline before touching the prose.
   - **Phase 2: Execution**: Deconstructs sections into independent writing tasks, generating them in parallel using LangGraph dynamic fan-out.
2. **Smart Routing Node**:
   - `closed_book`: Theoretical, established knowledge (bypasses search to conserve API quotas).
   - `open_book`: Time-sensitive or emerging topics requiring deep real-time web retrieval.
   - `hybrid`: Foundational concepts requiring modern real-world examples, libraries, or benchmarks.
3. **Dynamic Tavily Research Node**:
   - Generates 3 to 10 distinct, highly targeted queries.
   - Fetches authoritative snippets and structures them into a validated **Evidence Pack**.
4. **Parallel Worker Fan-Out**:
   - Replaces slow sequential generation with concurrent `Send("worker", ...)` calls.
   - Drastically cuts latency (reduces multi-section writing times by up to 70%).
5. **Real-time Cost & Token Tracker**:
   - Custom `TokenUsageCallbackHandler` tracks prompt tokens, completion tokens, and real-time USD cost per node.
6. **Multimodal Visual Reducer**:
   - Plans optimal image placements (up to 3 illustrations per post).
   - Generates vector-style illustrations via **Google Gemini Imagen 3** or **Hugging Face FLUX.1**.
   - Automatic local **Pillow procedural fallback** ensures image generation never crashes if API keys are missing.
7. **Dual-Interface Access**:
   - **Interactive Web App**: Streamlit GUI on port `8501`.
   - **FastAPI REST API**: High-performance backend on port `8000` with CORS support for modern frontends (e.g., Vercel, Next.js).

---

## 🏗️ Repository Structure

```text
FX_LangGraph/
├── docs/
│   └── interactive_flow.html      # 🌟 Standalone Archify interactive diagram
├── interactive_flow.html          # Root shortcut to the interactive visualizer
├── blog_agent/
│   ├── config.py                  # API key manager (OpenRouter, OpenAI, Tavily, Gemini)
│   ├── graph/
│   │   ├── state.py               # OverallState TypedDict & Pydantic schemas (Plan, Task, Evidence)
│   │   ├── llm.py                 # LLM client initialization (Nemotron / GPT-4o mini)
│   │   ├── workflow.py            # LangGraph state graph compilation & conditional edges
│   │   └── nodes/
│   │       ├── router.py          # Classifies knowledge requirement (closed/open/hybrid)
│   │       ├── research.py        # Tavily search query generator & evidence aggregator
│   │       ├── planner.py         # Structured outline orchestrator (Pydantic PlanObject)
│   │       ├── worker.py          # Parallel writer node
│   │       └── reducer.py         # Sequential stitcher, image planner, & markdown assembler
│   └── utils/
│       ├── tavily_client.py       # Tavily client with automatic mock fallback
│       ├── gemini_client.py       # Google Gemini Imagen API client
│       └── image_generator.py     # Multimodal engine (Gemini, FLUX, Pillow fallback)
├── app.py                         # Streamlit interactive dashboard (Port 8501)
├── api.py                         # FastAPI REST API with CORS (Port 8000)
├── Dockerfile                     # Multi-purpose production Dockerfile
├── .dockerignore                  # Prevents secret & cache leakage in Docker builds
├── DEPLOYMENT_GUIDE.md            # Step-by-step AWS EC2 (Free Tier) & Vercel deployment guide
├── requirements.txt               # Pinned Python dependencies
└── .env.example                   # Sanitized environment variable template
```

---

## ⚡ Quick Start (Local Setup)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/saket0x07/Agentic-blog-researcher-and-writter.git
cd Agentic-blog-researcher-and-writter

# Create virtual environment
python -m venv myenv

# Activate (Windows PowerShell)
.\myenv\Scripts\Activate.ps1

# Activate (macOS/Linux)
# source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the sample environment file:
```bash
cp .env.example .env
```

Configure your `.env` file:
```env
# Required LLM Key (choose one):
OPENROUTER_API_KEY=your_openrouter_key
# OPENAI_API_KEY=your_openai_key

# Optional (mock fallbacks used if omitted):
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key
```

> **Testing Without Paid Keys**: If `TAVILY_API_KEY` or `GEMINI_API_KEY` are not set, the pipeline automatically uses built-in mock web research and Pillow vector placeholders.

---

## 🚀 Running the Project

### Option A: Launch the Streamlit Web Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Option B: Launch the FastAPI REST Server
```bash
uvicorn api:app --reload --port 8000
```
- API Root: [http://localhost:8000](http://localhost:8000)
- Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API Endpoints Reference

| Method | Route | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Server health check | *None* |
| `POST` | `/blog/write` | Synchronously generates blog and returns summary | `{"topic": "string"}` |
| `POST` | `/generate` | Full generation with node-by-node token & cost breakdown | `{"topic": "string"}` |
| `GET` | `/docs` | Interactive Swagger UI | *Browser* |

#### Example cURL Request:
```bash
curl -X POST "http://localhost:8000/blog/write" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Explain Agentic AI Workflows with LangGraph"}'
```

---

## 🐳 Docker & Cloud Deployment

The repository is fully Dockerized and optimized for **AWS Free Tier (t2.micro)**.

### Run Pre-built Docker Image:
```bash
docker run -d \
  --name fx-agent-ui \
  -p 8501:8501 \
  --env-file .env \
  saket0x07/blog-agent:latest
```

### AWS EC2 & Vercel Deployment:
For comprehensive, zero-cost cloud deployment instructions (including 2GB Swap configuration for `t2.micro`, Nginx SSL setup, and Vercel proxy configuration), consult:
👉 **[Read DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
