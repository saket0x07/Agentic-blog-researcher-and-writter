import sys
from pathlib import Path

# Add parent directory of blog_agent to the python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import os
import re
from blog_agent.graph.workflow import blog_agent_graph
from blog_agent import config

# Page configuration
st.set_page_config(
    page_title="Automated Content Planner & Writer",
    page_icon="✍️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        color: #212529;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .status-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #ffffff;
        color: #1f2937;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #4A90E2;
    }
    .evidence-card {
        padding: 10px;
        margin-bottom: 8px;
        background-color: #1f2937;
        color: #f3f4f6;
        border-radius: 6px;
        font-size: 0.9em;
        border: 1px solid #374151;
    }
    .evidence-card a {
        color: #60a5fa;
        text-decoration: underline;
    }
    .evidence-card a:hover {
        color: #93c5fd;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title & Subtitle
st.title("✍️ Blog Planner & Writer")
st.markdown("Generate comprehensive, factual, research-backed blogs utilizing parallel LangGraph workflows, Tavily Search, and Gemini Image Generation.")

# Sidebar - Key configuration checks
st.sidebar.title("API Key Status")
st.sidebar.markdown("Checking environment variable configuration:")

keys = {
    "OpenRouter (LLM)": config.OPENROUTER_API_KEY,
    "OpenAI (LLM Fallback)": config.OPENAI_API_KEY,
    "Tavily (Search)": config.TAVILY_API_KEY,
    "Gemini/Google (Images)": config.GEMINI_API_KEY
}

for name, value in keys.items():
    if value:
        st.sidebar.success(f"✔️ {name} Configured")
    else:
        st.sidebar.warning(f"⚠️ {name} Missing (Using fallback/mock)")

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Fallback Mode:** If keys are missing, the agent will execute successfully "
    "using mock search data and Pillow local image placeholders."
)

# User Input
topic = st.text_input(
    "Enter the topic for your technical blog:",
    placeholder="e.g., How Self-Attention works in Transformer models"
)

# Execution block
if st.button("Generate Blog Post") and topic:
    # Reset/Create placeholders
    progress_bar = st.progress(0)
    status_text = st.empty()
    logs_container = st.container()
    
    # State tracking
    graph_inputs = {"topic": topic}
    evidence_pack = []
    generated_plan = None
    final_blog_content = None
    generated_images = []
    
    with logs_container:
        st.subheader("Workflow Execution Logs")
        
        # Stream the graph execution
        # Initialize steps count for simple progress display
        step_progress = 0
        total_steps = 5 # router, research (optional), planner, worker, reducer
        
        try:
            for event in blog_agent_graph.stream(graph_inputs, stream_mode="updates"):
                # Track nodes
                for node_name, output in event.items():
                    step_progress += 1
                    percent = min(int((step_progress / total_steps) * 100), 100)
                    progress_bar.progress(percent)
                    
                    if node_name == "router":
                        category = output.get("knowledge_category", "hybrid")
                        status_text.markdown(f"**Current Node:** Router completed. Category selected: `{category}`")
                        st.markdown(f"""
                        <div class="status-card">
                            <strong>Router Node:</strong> Topic classified as <strong>{category.upper()}</strong>.<br>
                            <em>Decision rationale:</em> Determined search needs based on topic complexity.
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif node_name == "research":
                        evidence_pack = output.get("evidence", [])
                        queries = output.get("search_queries", [])
                        status_text.markdown(f"**Current Node:** Research completed. Found {len(evidence_pack)} documents.")
                        
                        with st.expander(f"🔍 View Research Evidence ({len(evidence_pack)} items collected)"):
                            st.write(f"Search Queries Run: {queries}")
                            for item in evidence_pack:
                                st.markdown(f"""
                                <div class="evidence-card">
                                    <strong><a href="{item['url']}" target="_blank">{item['title']}</a></strong> ({item['date']})<br>
                                    {item['snippet']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                    elif node_name == "planner":
                        generated_plan = output.get("plan", {})
                        status_text.markdown(f"**Current Node:** Planner completed. Built section outlines.")
                        
                        with st.expander("📋 View Generated Content Plan"):
                            st.markdown(f"### Title: {generated_plan.get('title')}")
                            st.markdown(f"**Audience:** {generated_plan.get('audience')} | **Tone:** {generated_plan.get('tone')}")
                            st.markdown("#### Section Tasks:")
                            for task in generated_plan.get("tasks", []):
                                st.markdown(f"- **{task['title']}** (ID: `{task['id']}` - ~{task['target_word_count']} words)")
                                st.markdown(f"  *Goal:* {task['goal']}")
                                st.markdown(f"  *Points:* {', '.join(task['bullet_points'])}")
                                
                    elif node_name == "worker":
                        # We accumulate drafts
                        drafts = output.get("section_drafts", [])
                        status_text.markdown(f"**Current Node:** Parallel Workers completed generation.")
                        st.success(f"✍️ Section drafts completed! Fanned out to {len(drafts)} writer nodes in parallel.")
                        
                    elif node_name == "reducer":
                        final_blog_content = output.get("final_blog", "")
                        generated_images = output.get("images", [])
                        image_prompts = output.get("image_prompts", [])
                        status_text.markdown("**Current Node:** Reducer completed. Blog is stitched & illustrated!")
                        progress_bar.progress(100)
                        st.success("🎉 Blog Generation Process Complete!")
                        
                        if image_prompts:
                            with st.expander("🖼️ View Generated Image Prompts"):
                                for idx, p_item in enumerate(image_prompts):
                                    st.markdown(f"#### Image #{idx+1} (Section: `{p_item['section_id']}`)")
                                    st.markdown(f"**Prompt:**")
                                    st.code(p_item['prompt'])
                                    st.markdown(f"**Caption:** {p_item['caption']}")
                                    st.markdown(f"**Local Path:** `{p_item['image_path']}`")
                                    status_badge = "🟢 Success" if p_item.get("success", False) else "🔴 Failed"
                                    st.markdown(f"**Status:** {status_badge}")
                                    if idx < len(image_prompts) - 1:
                                        st.markdown("---")
                        
        except Exception as e:
            st.error(f"An error occurred during workflow execution: {e}")
            
    # Display Output Section if generated
    if final_blog_content:
        st.markdown("---")
        st.header("📄 Generated Blog Preview")
        
        title_slug = re.sub(r'[^a-zA-Z0-9]', '_', generated_plan.get('title', 'blog').lower())[:30]
        st.download_button(
            label="Download Markdown File",
            data=final_blog_content,
            file_name=f"{title_slug}_blog.md",
            mime="text/markdown"
        )
        

        parts = re.split(r'(!\[.*?\]\(.*?\))', final_blog_content)
        
        for part in parts:
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', part)
            if img_match:
                caption = img_match.group(1)
                img_path = img_match.group(2)
                
                full_path = Path(__file__).resolve().parent / img_path
                if full_path.exists():
                    st.image(str(full_path), caption=caption, use_column_width=True)
                else:
                    st.warning(f"Image not found at path: {img_path}")
            else:
                st.markdown(part)
