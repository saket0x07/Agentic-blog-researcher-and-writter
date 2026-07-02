import sys
from pathlib import Path

# Add parent directory of blog_agent to the python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import os
import re
from blog_agent.graph.workflow import blog_agent_graph
from blog_agent.graph.nodes.reducer import ImagePlan
from blog_agent.graph.llm import get_llm
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
    "using mock search data and Pillow local image# Initialize session state variables
if "workflow_stage" not in st.session_state:
    st.session_state.workflow_stage = "idle"
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}
if "proposed_images" not in st.session_state:
    st.session_state.proposed_images = []
if "image_choices" not in st.session_state:
    st.session_state.image_choices = []
if "final_blog_content" not in st.session_state:
    st.session_state.final_blog_content = None
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = []
if "topic" not in st.session_state:
    st.session_state.topic = ""

# Sidebar option to reset state
if st.sidebar.button("Clear App State & Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Stage 1: Idle - Input Topic and Run Draft Workflow
if st.session_state.workflow_stage == "idle":
    topic = st.text_input(
        "Enter the topic for your technical blog:",
        placeholder="e.g., How Self-Attention works in Transformer models"
    )

    if st.button("Plan & Draft Content") and topic:
        st.session_state.topic = topic
        progress_bar = st.progress(0)
        status_text = st.empty()
        logs_container = st.container()
        
        graph_inputs = {"topic": topic}
        evidence_pack = []
        generated_plan = None
        
        with logs_container:
            st.subheader("Workflow Execution Logs")
            step_progress = 0
            total_steps = 4 # router, research (optional), planner, worker
            
            try:
                for event in blog_agent_graph.stream(graph_inputs, stream_mode="updates"):
                    for node_name, output in event.items():
                        step_progress += 1
                        percent = min(int((step_progress / total_steps) * 100), 100)
                        progress_bar.progress(percent)
                        
                        # Accumulate state updates
                        st.session_state.graph_state.update(output)
                        
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
                            drafts = output.get("section_drafts", [])
                            status_text.markdown(f"**Current Node:** Parallel Workers completed generation.")
                            st.success(f"✍️ Section drafts completed! Fanned out to {len(drafts)} writer nodes in parallel.")
                            
                            # Plan images
                            st.info("🧠 Planning image placements based on drafted content...")
                            accumulated_state = dict(graph_inputs)
                            accumulated_state.update(st.session_state.graph_state)
                            accumulated_state.update(output)
                            
                            plan = accumulated_state.get("plan", {})
                            drafts_list = accumulated_state.get("section_drafts", [])
                            
                            # Stitch sections
                            task_order = {t["id"]: i for i, t in enumerate(plan.get("tasks", []))}
                            sorted_drafts = sorted(drafts_list, key=lambda x: task_order.get(x["task_id"], 999))
                            raw_blog_text = "\n\n".join([sec["content"] for sec in sorted_drafts])
                            
                            llm = get_llm()
                            structured_llm = llm.with_structured_output(ImagePlan)
                            system_prompt = (
                                "You are a technical editor. Your job is to review a compiled technical blog post "
                                "and determine up to 3 ideal sections to embed visuals. You will output a list of image items, "
                                "each specifying the section_id where the visual fits best, a detailed Imagen 3 generation prompt "
                                "describing the style (use professional, clean tech vector illustrations, avoid realistic photos), "
                                "and a caption for the graphic."
                            )
                            user_prompt = (
                                f"Blog Title: {plan['title']}\n"
                                f"Blog Structure (Tasks):\n"
                                f"{[{'id': t['id'], 'title': t['title'], 'goal': t['goal']} for t in plan['tasks']]}\n\n"
                                f"Stitched Content Preview:\n{raw_blog_text[:2000]}..."
                            )
                            
                            try:
                                image_plan = structured_llm.invoke([
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ])
                                proposed_images = []
                                for img in image_plan.images:
                                    proposed_images.append({
                                        "section_id": img.section_id,
                                        "prompt": img.prompt,
                                        "caption": img.caption,
                                        "mode": "generate"
                                    })
                                st.session_state.proposed_images = proposed_images
                                st.session_state.graph_state = accumulated_state
                                st.session_state.workflow_stage = "planned"
                                st.success("🖼️ Proposed images planned successfully!")
                                st.rerun()
                            except Exception as e:
                                st.warning(f"Failed to automatically plan images: {e}. Fallback to manual setup.")
                                st.session_state.proposed_images = []
                                st.session_state.graph_state = accumulated_state
                                st.session_state.workflow_stage = "planned"
                                st.rerun()
            except Exception as e:
                st.error(f"An error occurred during workflow execution: {e}")

# Stage 2: Planned - Interactive Form for Image Choices
elif st.session_state.workflow_stage == "planned":
    st.info(f"📝 **Topic:** {st.session_state.topic} | Content drafts and outlines generated!")
    
    st.markdown("---")
    st.header("🖼️ Step 2: Review & Approve Image Placements")
    st.write("Review the proposed image slots, optimize their prompts/captions, and select whether to generate using AI or fetch from the web.")
    
    with st.form("image_choices_form"):
        proposed = st.session_state.proposed_images
        updated_choices = []
        
        if not proposed:
            st.warning("No images planned by LLM. You can proceed without images or reset.")
        else:
            for idx, img in enumerate(proposed):
                st.subheader(f"Image Slot #{idx+1} (Proposed for Section: `{img['section_id']}`)")
                col1, col2 = st.columns([1, 2])
                with col1:
                    mode = st.radio(
                        f"Image Source Mode for slot #{idx+1}",
                        ["🎨 Generate using AI (Gemini / FLUX)", "🌐 Search & Fetch Web Image (Tavily)"],
                        index=0 if img.get("mode", "generate") == "generate" else 1,
                        key=f"mode_{idx}"
                    )
                    mode_val = "generate" if "Generate" in mode else "fetch"
                with col2:
                    prompt_val = st.text_area(
                        f"Prompt / Search Query for slot #{idx+1}",
                        value=img["prompt"],
                        height=100,
                        key=f"prompt_{idx}"
                    )
                    caption_val = st.text_input(
                        f"Caption for slot #{idx+1}",
                        value=img["caption"],
                        key=f"caption_{idx}"
                    )
                
                updated_choices.append({
                    "section_id": img["section_id"],
                    "prompt": prompt_val,
                    "caption": caption_val,
                    "mode": mode_val
                })
                st.markdown("---")
        
        submit_btn = st.form_submit_button("Assemble & Generate Final Illustrated Blog")
        
        if submit_btn:
            st.session_state.image_choices = updated_choices
            st.session_state.workflow_stage = "assembling"
            st.rerun()

# Stage 3: Assembling - Execute Reducer Node Directly
elif st.session_state.workflow_stage == "assembling":
    st.header("📄 Assembling & Illustrating Blog")
    status_placeholder = st.empty()
    status_placeholder.info("Running Reducer Node to download/generate images and stitch final markdown...")
    
    # Merge choices into final state
    final_state = dict(st.session_state.graph_state)
    final_state["image_choices"] = st.session_state.image_choices
    
    try:
        from blog_agent.graph.nodes.reducer import reducer_node
        output = reducer_node(final_state)
        
        st.session_state.final_blog_content = output.get("final_blog", "")
        st.session_state.generated_images = output.get("images", [])
        st.session_state.image_prompts = output.get("image_prompts", [])
        
        st.session_state.workflow_stage = "completed"
        st.rerun()
    except Exception as e:
        st.error(f"Failed during reducer execution: {e}")
        if st.button("Go Back"):
            st.session_state.workflow_stage = "planned"
            st.rerun()

# Stage 4: Completed - Display outputs
elif st.session_state.workflow_stage == "completed":
    st.success("🎉 Blog Generation Process Complete!")
    
    plan = st.session_state.graph_state.get("plan", {})
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("📋 View Content Plan"):
            st.markdown(f"### Title: {plan.get('title')}")
            st.markdown(f"**Audience:** {plan.get('audience')} | **Tone:** {plan.get('tone')}")
            st.markdown("#### Section Tasks:")
            for task in plan.get("tasks", []):
                st.markdown(f"- **{task['title']}** (ID: `{task['id']}` - ~{task['target_word_count']} words)")
                st.markdown(f"  *Goal:* {task['goal']}")
    with col2:
        image_prompts = st.session_state.image_prompts
        if image_prompts:
            with st.expander("🖼️ View Generated/Fetched Image Prompts"):
                for idx, p_item in enumerate(image_prompts):
                    st.markdown(f"#### Image #{idx+1} (Section: `{p_item['section_id']}`)")
                    st.markdown(f"**Mode:** `{p_item.get('mode', 'generate')}`")
                    st.markdown(f"**Prompt/Query:**")
                    st.code(p_item['prompt'])
                    st.markdown(f"**Caption:** {p_item['caption']}")
                    st.markdown(f"**Local Path:** `{p_item['image_path']}`")
                    if p_item.get("source_url"):
                        st.markdown(f"**Source Credit:** [Link]({p_item['source_url']})")
                    status_badge = "🟢 Success" if p_item.get("success", False) else "🔴 Failed"
                    st.markdown(f"**Status:** {status_badge}")
                    if idx < len(image_prompts) - 1:
                        st.markdown("---")

    st.markdown("---")
    st.header("📄 Generated Blog Preview")
    
    title_slug = re.sub(r'[^a-zA-Z0-9]', '_', plan.get('title', 'blog').lower())[:30]
    st.download_button(
        label="Download Markdown File",
        data=st.session_state.final_blog_content,
        file_name=f"{title_slug}_blog.md",
        mime="text/markdown"
    )
    
    parts = re.split(r'(!\[.*?\]\(.*?\))', st.session_state.final_blog_content)
    for part in parts:
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', part)
        if img_match:
            caption = img_match.group(1)
            img_path = img_match.group(2)
            
            full_path = Path(__file__).resolve().parent / img_path
            if full_path.exists():
                st.image(str(full_path), caption=caption, use_column_width=True)
            else:
                if Path(img_path).exists():
                    st.image(img_path, caption=caption, use_column_width=True)
                else:
                    st.warning(f"Image not found at path: {img_path}")
        else:
            st.markdown(part)
