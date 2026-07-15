from typing import List
from pydantic import BaseModel, Field
from blog_agent.graph.state import OverallState
from blog_agent.graph.llm import get_llm
from blog_agent.utils.tavily_client import search_tavily

class QueryGenerator(BaseModel):
    queries: List[str] = Field(
        description="A list of 3 to 10 highly specific search queries to gather comprehensive facts and data about the topic."
    )

def research_node(state: OverallState):
    """
    Generates search queries, executes them on Tavily, and compiles the evidence pack.
    """
    topic = state["topic"]
    llm = get_llm()
    
    print(f"[Research Node] Generating search queries for topic: '{topic}'")
    
    # 1. Generate search queries using LLM
    structured_llm = llm.with_structured_output(QueryGenerator)
    system_prompt = (
        "You are an expert technical researcher. Your goal is to take a blog topic and generate "
        "between 3 and 10 search queries. These queries should target recent news, technical specifications, "
        "industry standards, code examples, or comparisons to build an accurate and detailed knowledge base."
    )
    user_prompt = f"Blog Topic: {topic}"
    
    try:
        query_result = structured_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        queries = query_result.queries
    except Exception as e:
        print(f"[Research Node] Error generating queries: {e}. Using default queries.")
        queries = [topic, f"{topic} latest updates", f"{topic} overview tutorial"]
        
    print(f"[Research Node] Generated queries: {queries}")
    
    # 2. Execute Tavily search for each query
    evidence_pack = []
    seen_urls = set()
    
    for query in queries:
        print(f"[Research Node] Searching for: '{query}'...")
        results = search_tavily(query, max_results=3)
        for item in results:
            url = item.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                evidence_pack.append(item)
                
    print(f"[Research Node] Finished research. Collected {len(evidence_pack)} unique evidence items.")
    return {
        "search_queries": queries,
        "evidence": evidence_pack
    }
