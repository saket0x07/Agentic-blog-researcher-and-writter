# Agentic AI for Automated Content Generation via LangGraph

This directory contains a complete implementation of a **Planning Agent** workflow for automated technical blog generation. Built using **LangGraph**, **LangChain**, and **Streamlit**, it implements the architecture outlined in the technical briefing.

## Key Features

1. **Two-Phase Execution Model**:
   * **Phase 1: Planning**: Analyzes the topic, dynamically determines research requirements, and generates a structured, multi-section plan using strict Pydantic schemas.
   * **Phase 2: Execution**: Writes section drafts in parallel utilizing LangGraph's dynamic fan-out mechanism, compiles the drafts, plans illustration inserts, generates images, and embeds visual content.
2. **Smart Routing Node**: Classifies queries into `closed_book` (theoretical/static), `open_book` (highly volatile/recent), and `hybrid` (concepts needing updated examples/statistics) to optimize search usage.
3. **Dynamic Tavily Research Node**: Formulates 3-10 distinct research queries, searches the web via Tavily, aggregates the results, and structures them into an "Evidence Pack" passed to the planner and workers.
4. **Parallel Worker Nodes**: Spawns concurrent worker nodes for each section, drastically reducing generation latency.
5. **Multimodal Reducer Node**: Joins section contents sequentially, plans image inserts (up to 3), generates visuals using Google Gemini's Imagen API (with Pillow placeholders fallback), and saves outputs.
6. **Polished Streamlit GUI**: Real-time progress monitoring, logs inspection, content plans expansion, inline image previewing, and one-click markdown exports.

---

## File Structure

```text
blog_agent/
├── README.md                  # Project overview, installation, and usage
├── requirements.txt           # Python dependencies
├── config.py                  # Environment loader (OpenRouter, Tavily, Gemini)
├── app.py                     # Streamlit frontend application
├── graph/
│   ├── __init__.py
│   ├── state.py               # Graph State & Pydantic models (Plan, Task, Evidence)
│   ├── llm.py                 # Core LLM initialization wrapper (supports OpenRouter/OpenAI)
│   ├── workflow.py            # LangGraph workflow definition & compilation
│   └── nodes/
│       ├── __init__.py
│       ├── router.py          # Classifies topic requirements
│       ├── research.py        # tavily research engine
│       ├── planner.py         # Orchestrator (Pydantic plan outline generator)
│       ├── worker.py          # Parallel writer node
│       └── reducer.py         # Stitches text, generates images, saves final markdown
└── utils/
    ├── __init__.py
    ├── tavily_client.py       # Tavily client and stub mock utility
    └── gemini_client.py       # Google Gemini Imagen API client and Pillow placeholder fallback
```

---

## Installation & Setup

1. **Configure Environment Variables**:
   Make sure you have a `.env` file in the root workspace (`d:\Fxis.ai\FX_LangGraph\.env`) or in this folder (`blog_agent/.env`) containing:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key   # For LLM (GPT-4o mini via OpenRouter)
   # Or standard OpenAI key:
   # OPENAI_API_KEY=your_openai_api_key
   
   TAVILY_API_KEY=your_tavily_api_key           # Optional: For web research
   GEMINI_API_KEY=your_gemini_api_key           # Optional: For image generation
   ```
   *Note: If Tavily or Gemini keys are missing, the system will fall back to mockup search content and local Pillow placeholder images, allowing you to test execution completely free.*

2. **Install Dependencies**:
   Navigate to the root workspace and run:
   ```bash
   pip install -r blog_agent/requirements.txt
   ```

3. **Launch the Streamlit GUI**:
   Run the Streamlit server:
   ```bash
   streamlit run blog_agent/app.py
   ```

---

## Technical Stack

* **LangGraph**: Stateful multi-agent graph flows, map-reduce fan-out, and execution loops.
* **LangChain & ChatOpenAI**: Chat prompts structure, structured model outputs via `with_structured_output`, and model invocation.
* **Pydantic (v2)**: State and output schema enforcement.
* **Tavily Search**: Optimized LLM search queries.
* **Google Gemini API**: Imagen 3 image generation.
* **Streamlit**: Single-page frontend dashboard.
