from typing import List, Dict, Any
from typing_extensions import TypedDict
from blog_agent.graph.llm import get_llm

# Define the local state shape passed to each worker during fan-out
class WorkerState(TypedDict):
    task: Dict[str, Any]
    title: str
    audience: str
    tone: str
    evidence: List[Dict[str, Any]]

def worker_node(state: WorkerState):
    """
    Worker node. Writes a single section of the blog post based on its specific task definition
    and context.
    """
    task = state["task"]
    overall_title = state["title"]
    audience = state["audience"]
    tone = state["tone"]
    evidence = state.get("evidence", [])
    
    task_id = task["id"]
    section_title = task["title"]
    goal = task["goal"]
    bullets = task["bullet_points"]
    word_count = task["target_word_count"]
    citations = task.get("requires_citations", False)
    code_blocks = task.get("requires_code_blocks", False)
    
    print(f"[Worker Node - {task_id}] Drafting section: '{section_title}'")
    
    # Format evidence for writing
    evidence_str = ""
    if evidence:
        evidence_str = "\nAvailable Research and Sources for Reference:\n"
        for i, item in enumerate(evidence):
            evidence_str += f"Source [{i+1}]: {item['title']}\nURL: {item['url']}\nSnippet: {item['snippet']}\n\n"
            
    system_prompt = (
        "You are an expert technical content writer. Your task is to draft a single section of a technical blog post.\n\n"
        f"Overall Blog Title: {overall_title}\n"
        f"Target Audience: {audience}\n"
        f"Writing Tone: {tone}\n\n"
        "Drafting Rules:\n"
        "1. Write ONLY the section content. Do not include introductory headers like '# Blog Title' or concluding remarks for the entire blog. "
        "Include the section title as a Markdown header (e.g. '## Section Title').\n"
        "2. Keep the content focused on the goal and ensure you cover all requested bullet points.\n"
        f"3. Aim for approximately {word_count} words.\n"
        "4. Follow professional, technical Markdown formatting.\n"
    )
    
    if citations:
        system_prompt += (
            "5. CRITICAL: You must cite facts by using standard hyperlinks inline. Format citations as [Source Title](URL). "
            "Use only the URLs provided in the research sources. Do not make up URLs."
        )
    else:
        system_prompt += "5. You do not need to cite sources for this section unless highly relevant."
        
    if code_blocks:
        system_prompt += (
            "\n6. CRITICAL: Include code blocks or technical configurations relevant to this section using proper Markdown syntax "
            "(e.g., ```python, ```bash, etc.)."
        )
        
    user_prompt = (
        f"Section to Draft: {section_title}\n"
        f"Goal: {goal}\n"
        f"Specific points to cover: {bullets}\n"
        f"{evidence_str}"
    )
    
    llm = get_llm()
    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        content = response.content
        
        print(f"[Worker Node - {task_id}] Finished draft ({len(content.split())} words).")
        return {
            "section_drafts": [{
                "task_id": task_id,
                "title": section_title,
                "content": content
            }]
        }
    except Exception as e:
        print(f"[Worker Node - {task_id}] Error drafting section: {e}")
        # Return a fallback draft
        fallback_content = (
            f"## {section_title}\n\n"
            f"*Drafting error occurred for task {task_id}: {str(e)}.*\n\n"
            f"Goal: {goal}\n"
        )
        return {
            "section_drafts": [{
                "task_id": task_id,
                "title": section_title,
                "content": fallback_content
            }]
        }
    
