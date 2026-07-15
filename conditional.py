from dotenv import load_dotenv
import os
from typing import TypedDict

from langgraph.graph import StateGraph , START , END
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model="google/gemma-4-26b-a4b-it:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    temperature=0.7
)

class SupportState(TypedDict):
    query: str
    category: str
    response: str

def classify_query(state: SupportState):
    prompt = f"""
    Classify the following query:
    - billing
    - technical
    - response

    {state['query']}
    """
    response = llm.invoke(prompt)
    category = response.content.strip().lower()
    return {"category" : category}

def billing_agent(state: SupportState):
    prompt = f"""
    Generate a response for the following query:
    {state['query']}
    """
    response = llm.invoke(prompt)
    return {"response" : response.content}

def technical_agent(state: SupportState):
    prompt = f"""
    Generate a response for the following query:
    {state['query']}
    """
    response = llm.invoke(prompt)
    return {"response" : response.content}

def general_agent(state: SupportState):
    prompt = f"""
    Generate a response for the following query:
    {state['query']}
    """
    response = llm.invoke(prompt)
    return {"response" : response.content}


def router(state):
    category = state["category"].strip().lower()
    if "billing" in category:
        return "billing_agent"
    elif "technical" in category:
        return "technical_agent"
    else:
        return "general_agent"

build = StateGraph(SupportState)

build.add_node("classify_query", classify_query)
build.add_node("billing_agent", billing_agent)
build.add_node("technical_agent", technical_agent)
build.add_node("general_agent", general_agent)

build.add_edge(START, "classify_query")
build.add_conditional_edges("classify_query", router, {
    "billing": "billing_agent",
    "technical": "technical_agent",
    "general": "general_agent"
})

build.add_edge("billing_agent", END)
build.add_edge("technical_agent", END)
build.add_edge("general_agent", END)

graph = build.compile()

if __name__ == "__main__":
    result = graph.invoke({"query" : "How can i get refund"})
    print(result["response"])
