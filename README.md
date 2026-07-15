# 🤖 Agentic Blog Researcher & Writer

> **Automated, research-backed technical blog generation powered by LangGraph, LLMs, and multi-modal AI**

Generate comprehensive, well-researched technical blog posts automatically with a two-phase agentic workflow. This project combines planning agents, parallel content writers, web research, and image generation to produce polished, illustrated markdown blogs in minutes.

---

## 🎯 Overview

The **Agentic Blog Researcher & Writer** is a sophisticated content generation system that orchestrates multiple AI agents to produce technical blogs from scratch. Instead of writing content sequentially, it:

1. **Analyzes** your topic and determines research requirements
2. **Researches** using web search to gather evidence and examples
3. **Plans** a structured, multi-section outline with specific writing tasks
4. **Generates** sections in parallel for speed and consistency
5. **Illustrates** with AI-generated or web-fetched images
6. **Compiles** everything into a polished markdown blog

### What Makes It Different?

- 🚀 **Parallel Execution**: Writes multiple sections simultaneously using LangGraph's map-reduce pattern
- 🧠 **Intelligent Routing**: Classifies topics as `closed_book`, `open_book`, or `hybrid` to optimize research strategy
- 🔍 **Smart Research**: Dynamically generates 3–10 targeted Tavily search queries and aggregates evidence
- 🎨 **Multimodal Output**: Embeds AI-generated images or web-fetched visuals with captions
- 💾 **Blog History**: SQLite database tracks all generated blogs for easy retrieval
- 🎛️ **Interactive UI**: Real-time monitoring, evidence review, image approval, and one-click exports via Streamlit

---

## ✨ Key Features

### 1. **Two-Phase Execution Model**

#### Phase 1: Planning & Research
- **Smart Router Node**: Classifies topics into:
  - `closed_book`: Theoretical/static content (minimal research needed)
  - `open_book`: Highly volatile/recent topics (extensive research required)
  - `hybrid`: Concepts needing updated examples and statistics
- **Dynamic Research Node**: Formulates 3–10 distinct Tavily search queries, aggregates results into an **Evidence Pack**
- **Planner Node**: Generates a structured plan with sections, goals, bullet points, and target word counts using Pydantic schemas

#### Phase 2: Content Generation & Assembly
- **Parallel Worker Nodes**: Each section spawned as a concurrent task, drastically reducing latency
- **Multimodal Reducer Node**: Stitches sections, plans image placements (up to 3), generates/fetches visuals, and saves final markdown
- **Image Generation**: Uses Google Gemini Imagen API or Hugging Face FLUX; falls back to Pillow placeholders if keys are missing

### 2. **Interactive Streamlit GUI**

- ✅ Real-time workflow execution with progress bars and logs
- ✅ Evidence inspection: View all research sources with links and snippets
- ✅ Content plan expansion: Review generated outline before writing
- ✅ Image approval workflow: Customize prompts, captions, and acquisition mode
- ✅ Blog history sidebar: Access previously generated blogs with one click
- ✅ Markdown export: Download blogs ready for publication

### 3. **Flexible API Support**

- **LLM Models**: OpenRouter (default) or OpenAI API for maximum flexibility
- **Research**: Tavily Search or mock fallback
- **Image Generation**: Google Gemini Imagen API, Hugging Face FLUX, or Pillow placeholders
- **No mandatory API keys**: Test the full system with fallbacks completely free

### 4. **Production-Ready Architecture**

- **LangGraph**: Stateful agentic workflows with conditional branching and map-reduce patterns
- **Pydantic v2**: Strict type validation for plan, evidence, and image schemas
- **Environment-based Config**: Load API keys from `.env` or environment variables
- **Error Handling**: Graceful fallbacks and detailed error messages throughout

---

## 🏗️ Architecture & File Structure

```
Agentic-blog-researcher-and-writter/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── config.py                          # Environment loader & API key management
├── app.py                             # Streamlit UI frontend
├── blog_agent/
│   ├── __init__.py
│   ├── config.py                      # Configuration (API keys, LLM settings)
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py                   # GraphState, Pydantic models (Plan, Task, Evidence)
│   │   ├── llm.py                     # LLM initialization & wrapper (OpenRouter/OpenAI)
│   │   ├── workflow.py                # LangGraph workflow compilation & execution
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── router.py              # Topic classification node (closed/open/hybrid)
│   │       ├── research.py            # Tavily research + evidence aggregation
│   │       ├── planner.py             # Plan generation with Pydantic schemas
│   │       ├── worker.py              # Parallel section writer node
│   │       └── reducer.py             # Image planning, generation/fetching, markdown assembly
│   └── utils/
│       ├── __init__.py
│       ├── tavily_client.py           # Tavily API client & mock search utility
│       ├── gemini_client.py           # Google Gemini Imagen API & Pillow fallback
│       ├── flux_client.py             # Hugging Face FLUX image generation
│       └── history_db.py              # SQLite blog history database
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+**
- **pip** or **conda**
- At least one LLM API key (OpenRouter or OpenAI)

### Step 1: Clone the Repository

```bash
git clone https://github.com/saket0x07/Agentic-blog-researcher-and-writter.git
cd Agentic-blog-researcher-and-writter
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```env
# LLM Configuration (Required - choose one)
OPENROUTER_API_KEY=your_openrouter_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Research Configuration (Optional - uses mock fallback if missing)
TAVILY_API_KEY=your_tavily_api_key_here

# Image Generation Configuration (Optional - uses Pillow fallback if missing)
GEMINI_API_KEY=your_google_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# LLM Model Selection (Optional)
LLM_MODEL=gpt-4o-mini  # Default: gpt-4o-mini via OpenRouter
```

**Why Fallbacks Matter:**
- Missing `TAVILY_API_KEY`? Uses mock search with pre-generated evidence
- Missing `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY`? Generates colorful Pillow placeholder images
- Missing `OPENROUTER_API_KEY`? Falls back to `OPENAI_API_KEY` (if configured)

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Launch the Application

```bash
streamlit run app.py
```

The Streamlit UI will open at `http://localhost:8501`. You're ready to generate blogs! 🚀

---

## 💻 Usage Guide

### Basic Workflow

1. **Enter a Topic**: Type your blog topic in the text input (e.g., "How Self-Attention Works in Transformers")
2. **Plan & Draft**: Click "Plan & Draft Content" to start the workflow
   - Router classifies topic requirements
   - Research node (if needed) gathers web evidence
   - Planner generates section outline
   - Workers write sections in parallel
3. **Review Plan & Evidence**: Expand collapsible cards to inspect research and structure
4. **Approve Images**: Customize AI image prompts and captions
5. **Choose Image Mode**: Select between FLUX generation or web image fetching
6. **Generate Final Blog**: Click "Assemble & Generate Final Illustrated Blog"
7. **Download or Save**: Export as markdown or view in history sidebar

### Example Topics to Try

✅ How do Large Language Models work?  
✅ Best Practices for Microservices Architecture  
✅ Introduction to Quantum Computing  
✅ Python Async/Await Explained  
✅ The Evolution of Neural Network Architectures  

---

## 🔧 Technical Stack

### Core Libraries

| Library | Purpose |
|---------|---------|
| **LangGraph** | Stateful agentic workflow orchestration with map-reduce patterns |
| **LangChain** | Prompt templates, structured outputs, LLM abstraction layer |
| **Pydantic** | Type validation for Plan, Task, Evidence, and Image schemas |
| **Streamlit** | Interactive web UI with real-time progress monitoring |
| **Tavily** | Web search API for research evidence aggregation |
| **Google GenAI** | Imagen 3 API for image generation |
| **Hugging Face** | FLUX model for alternative image generation |
| **Pillow** | Fallback placeholder image creation |
| **Python-dotenv** | Environment variable management |

### AI Models

- **LLM**: GPT-4o mini (via OpenRouter) or OpenAI GPT-4
- **Image Gen**: Google Gemini Imagen 3 or Hugging Face FLUX
- **Search**: Tavily Search API

---

## 📋 Pydantic Schemas

### Plan Schema
```python
class Plan(BaseModel):
    title: str                  # Blog title
    audience: str               # Target audience
    tone: str                   # Writing tone (professional, casual, etc.)
    tasks: list[Task]           # List of section writing tasks
```

### Task Schema
```python
class Task(BaseModel):
    id: str                     # Unique task ID
    title: str                  # Section title
    goal: str                   # Writing objective
    bullet_points: list[str]    # Key points to cover
    target_word_count: int      # Expected section length
```

### Evidence Schema
```python
class Evidence(BaseModel):
    title: str                  # Source title
    url: str                    # Source URL
    snippet: str                # Relevant excerpt
    date: str                   # Publication date
```

### ImagePlan Schema
```python
class ImageItem(BaseModel):
    section_id: str             # Target section for image
    prompt: str                 # Generation/search prompt
    caption: str                # Image caption in blog
    search_query: str           # Web search fallback query
```

---

## 🌐 API Configuration

### OpenRouter (Recommended)
```python
# Supports 200+ models with fallback handling
# Get API key: https://openrouter.ai/
OPENROUTER_API_KEY=sk-or-...
```

### OpenAI (Fallback)
```python
# Direct OpenAI endpoint
# Get API key: https://platform.openai.com/
OPENAI_API_KEY=sk-...
```

### Tavily Search
```python
# Web research API
# Get API key: https://tavily.com/
TAVILY_API_KEY=tvly-...
```

### Google Gemini
```python
# Imagen 3 image generation
# Get API key: https://aistudio.google.com/
GEMINI_API_KEY=AIzaSy...
```

### Hugging Face (FLUX)
```python
# FLUX model for image generation
# Get token: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=hf_...
```

---

## 🎯 Workflow Execution Details

### Phase 1: Analysis & Planning

```
┌─────────────┐
│   Input     │
│   Topic     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ Router Node                 │
│ (Classify: closed/open/hybrid) │
└──────┬──────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Research Node (Conditional)  │
│ (If open_book or hybrid)     │
│ - Generate queries           │
│ - Tavily search              │
│ - Aggregate Evidence Pack    │
└──────┬───────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ Planner Node                   │
│ - Parse evidence               │
│ - Generate structured plan     │
│ - Define sections & tasks      │
└──────┬─────────────────────────┘
       │
       ▼
   (Plan Ready)
```

### Phase 2: Parallel Generation & Assembly

```
┌──────────────┐
│  Plan Ready  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Fan-Out: Spawn Worker Nodes         │
│ (One per section, parallel)         │
│ - Worker 1: Intro                   │
│ - Worker 2: Core Concepts           │
│ - Worker 3: Examples & Use Cases    │
│ - Worker 4: Conclusion              │
└──────┬──────────────────────────────┘
       │
       ▼
   (All sections drafted)
       │
       ▼
┌──────────────────────────────┐
│ Reducer Node                 │
│ - Stitch sections in order   │
│ - Plan image placements      │
│ - Generate/fetch images      │
│ - Embed in markdown          │
│ - Save to disk               │
└──────┬───────────────────────┘
       │
       ▼
   (Final Illustrated Blog)
```

---

## 🖼️ Image Generation Workflow

### Mode 1: Generate with FLUX
1. Receives structured image prompts from planner
2. Sends to Hugging Face FLUX API
3. Saves generated images to `blog_agent/outputs/images/`
4. Embeds in markdown with captions

### Mode 2: Search & Fetch
1. Sends search queries to Tavily Search
2. Retrieves relevant image URLs
3. Downloads and caches locally
4. Embeds with proper attribution

### Fallback: Pillow Placeholders
1. If APIs are unavailable, generates colored placeholder images
2. Includes text overlay with prompt
3. Useful for testing without API keys

---

## 📊 Real-Time Monitoring

The Streamlit UI provides:

- **Progress Bars**: Overall workflow completion percentage
- **Execution Logs**: Node-by-node status updates
- **Evidence Cards**: Dark-themed research source cards with links
- **Plan Expansion**: View full section outlines, goals, and bullet points
- **Image Preview**: Inline display of generated/fetched images
- **Error Handling**: Clear error messages with recovery suggestions

---

## 💾 Blog History & Storage

All generated blogs are:
1. **Saved Locally**: Markdown files in `blog_agent/outputs/blogs/`
2. **Indexed in SQLite**: Database at `blog_agent/db/blogs.db`
3. **Accessible via Sidebar**: One-click retrieval of past generations
4. **Downloadable**: Export as markdown or view in browser

**View Blog History:**
```python
from blog_agent.utils.history_db import get_all_blogs, get_blog_by_id

# Get all blogs
all_blogs = get_all_blogs()

# Get specific blog by ID
blog = get_blog_by_id(blog_id)
```

---

## 🐛 Troubleshooting

### Issue: "API Key Missing" Error

**Solution**: Ensure your `.env` file is in the project root and has the correct format. Restart the Streamlit app:
```bash
streamlit run app.py
```

### Issue: No Research Results / Mock Data

**Cause**: Tavily API key is missing or invalid.  
**Solution**: Add a valid `TAVILY_API_KEY` or allow the system to use mock search data for testing.

### Issue: No Images Generated

**Cause**: Both Gemini and FLUX API keys are missing.  
**Solution**: Add valid API keys or allow Pillow placeholder generation.

### Issue: Slow Workflow Execution

**Cause**: Worker nodes may take time for longer sections or if API rate limits are hit.  
**Solution**: Check API rate limits and wait for completion. The progress bar shows overall status.

### Issue: Image Paths Not Found in Rendered Blog

**Cause**: Relative image paths may be broken in certain environments.  
**Solution**: Use absolute paths or ensure the `blog_agent/outputs/images/` directory is in the right location.

---

## 🔐 Security & Best Practices

- ✅ **Never commit `.env`**: Add to `.gitignore`
- ✅ **Rotate API keys regularly**: Especially after public commits
- ✅ **Use environment variables in production**: Don't hardcode keys
- ✅ **Validate API responses**: Error handling prevents cascading failures
- ✅ **Rate limiting**: Respect API quotas (especially for Tavily and Gemini)

---

## 🚀 Performance Tips

1. **Parallel Execution**: Worker nodes run concurrently. Parallel speedup is ~N sections / 1 sequential.
2. **API Batching**: Tavily queries are batched; limit to 3–5 per research phase.
3. **Image Caching**: Downloaded images are cached locally to avoid re-fetching.
4. **Timeout Handling**: Long-running tasks have 5-minute timeouts; adjust in `workflow.py` if needed.

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Support for additional LLMs (Anthropic Claude, Ollama)
- [ ] PDF export format
- [ ] Multi-language support
- [ ] SEO optimization layer
- [ ] Citation & bibliography auto-generation
- [ ] Publishing integrations (Medium, Dev.to, Hashnode)

---

## 📄 License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 📞 Support & Contact

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for ideas and feedback
- **Email**: Contact the author via GitHub profile

---

## 🎓 Learning Resources

### LangGraph & LangChain
- [LangGraph Official Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)

### AI Models & APIs
- [OpenRouter Docs](https://openrouter.ai/docs)
- [Tavily Search API](https://tavily.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Hugging Face Models](https://huggingface.co/models)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)

---

## 🙏 Acknowledgments

- **LangGraph** team for the powerful agentic workflow framework
- **LangChain** for prompt engineering and LLM abstractions
- **Tavily** for web research capabilities
- **Google Gemini** for image generation API
- **Streamlit** for the amazing UI framework

---

## 📊 Future Roadmap

- [ ] **v2.0**: Multi-language blog generation
- [ ] **v2.0**: SEO optimization with keyword insertion
- [ ] **v2.1**: Email newsletter auto-generation
- [ ] **v2.2**: Blog analytics dashboard
- [ ] **v3.0**: Integration with popular CMS platforms (WordPress, Ghost)
- [ ] **v3.0**: Video script & podcast outline generation

---

**Happy blogging! 🚀✍️📝**

Generated with ❤️ using LangGraph and AI agents.
