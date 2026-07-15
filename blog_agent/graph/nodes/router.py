from pydantic import BaseModel, Field
from blog_agent.graph.state import OverallState
from blog_agent.graph.llm import get_llm

class RoutingDecision(BaseModel):
    category: str = Field(
        description="The knowledge category. Must be one of: 'closed_book', 'open_book', 'hybrid'."
    )
    rationale: str = Field(
        description="Short reason explaining why this category was selected."
    )

def router_node(state: OverallState):
    """
    Analyzes the blog topic to determine if external research is needed.
    """
    topic = state["topic"]
    llm = get_llm()
    
    # Binding structured output
    structured_llm = llm.with_structured_output(RoutingDecision)
    
    system_prompt = (
        "You are an expert content strategist router. Your task is to analyze the user's blog topic "
        "and classify it into one of three knowledge categories:\n\n"
        "1. 'closed_book': Standard, well-documented, or theoretical concepts that the LLM already knows in depth. "
        "No real-time web research is required (e.g., 'What is Self-Attention').\n"
        "2. 'open_book': Highly volatile, news-oriented, or very recent topics requiring current internet search data "
        "to be accurate (e.g., 'Top AI News of the Week').\n"
        "3. 'hybrid': Concepts where the LLM understands the core theory but needs updated examples, latest frameworks, "
        "or specific recent stats to be comprehensive and modern (e.g., 'State of Open Source LLMs in 2026').\n\n"
        "Provide a classification and a brief rationale."
    )
    
    user_prompt = f"Blog Topic: {topic}"
    
    try:
        decision = structured_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        category = decision.category.strip().lower()
        if category not in ["closed_book", "open_book", "hybrid"]:
            category = "hybrid" # Fallback
            
        print(f"[Router Node] Classed topic '{topic}' as: '{category}' (Rationale: {decision.rationale})")
        return {"knowledge_category": category}
    except Exception as e:
        print(f"[Router Node] Error during routing: {e}. Defaulting to 'hybrid'.")
        return {"knowledge_category": "hybrid"}
