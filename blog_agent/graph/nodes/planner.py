from blog_agent.graph.state import OverallState, PlanObject
from blog_agent.graph.llm import get_llm

def planner_node(state: OverallState):
    """
    Orchestrator node. Generates the structured outline and plan for the blog post.
    """
    topic = state["topic"]
    evidence = state.get("evidence", [])
    category = state.get("knowledge_category", "hybrid")
    llm = get_llm()
    
    print(f"[Planner Node] Generating blog plan for topic: '{topic}' in category: '{category}'")
    
    # Format evidence for the prompt if available
    evidence_str = ""
    if evidence:
        evidence_str = "\nAvailable Research/Evidence:\n"
        for i, item in enumerate(evidence):
            evidence_str += f"[{i+1}] Title: {item['title']}\nURL: {item['url']}\nSnippet: {item['snippet']}\n\n"
            
    system_prompt = (
        "You are an expert technical blog publisher and orchestrator. "
        "Your task is to take a blog topic, check any available research/evidence, and produce "
        "a highly structured blog outline (Plan). You must break down the blog into sequential sections (Tasks).\n\n"
        "Guidelines for the Plan:\n"
        "1. Create a logical progression (e.g., Intro, Core Architecture/Concepts, Detailed Walkthrough/Code, Future/Conclusion).\n"
        "2. For each section, define an ID (e.g. 'sec_1'), title, goal, bullet points to cover, and a target word count.\n"
        "3. Specify requirements like citations (if it needs to refer to URLs in research) or code blocks (if it is a technical tutorial).\n"
        "4. Keep the plan professional, clear, and focused on the target audience and tone."
    )
    
    user_prompt = f"Topic: {topic}\nKnowledge Category: {category}\n{evidence_str}"
    
    # Generate structured output using Pydantic PlanObject
    structured_llm = llm.with_structured_output(PlanObject)
    
    try:
        plan_obj = structured_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # Convert Pydantic object to dict to store in graph state
        plan_dict = plan_obj.model_dump()
        print(f"[Planner Node] Successfully created plan '{plan_dict['title']}' with {len(plan_dict['tasks'])} tasks.")
        return {"plan": plan_dict}
        
    except Exception as e:
        print(f"[Planner Node] Error creating plan: {e}. Falling back to default skeleton plan.")
        # Fallback skeleton plan
        fallback_plan = {
            "title": f"Complete Guide to {topic}",
            "audience": "Technical Professionals",
            "tone": "Technical and Informative",
            "tasks": [
                {
                    "id": "sec_1",
                    "title": f"Introduction to {topic}",
                    "goal": "Introduce the topic and explain why it matters.",
                    "bullet_points": ["Definition of topic", "Key concepts", "Historical context"],
                    "target_word_count": 250,
                    "requires_citations": False,
                    "requires_code_blocks": False
                },
                {
                    "id": "sec_2",
                    "title": "Core Implementation Details",
                    "goal": "Explain how this technology works under the hood.",
                    "bullet_points": ["Step-by-step logic", "Architecture breakdown"],
                    "target_word_count": 400,
                    "requires_citations": True,
                    "requires_code_blocks": True
                },
                {
                    "id": "sec_3",
                    "title": "Conclusion and Next Steps",
                    "goal": "Summarize the key takeaways and future outlook.",
                    "bullet_points": ["Takeaways summary", "Future evolution"],
                    "target_word_count": 200,
                    "requires_citations": False,
                    "requires_code_blocks": False
                }
            ]
        }
        return {"plan": fallback_plan}
