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

class MarketingState(TypedDict):
    topic:str
    keywords:str
    caption:str

def generate_keywords(state:MarketingState):
    prompt = f"""
    Generate keywords for the following topic:
    {state['topic']}
    """
    response = llm.invoke(prompt)
    return {"keywords" : response.content}

def generate_caption(state:MarketingState):
    prompt = f"""
    Generate a caption for the following topic:
    Topic: {state['topic']}
    """
    response = llm.invoke(prompt)
    return {"caption" : response.content}


builder = StateGraph(MarketingState)

builder.add_node("generate_keywords", generate_keywords)
builder.add_node("generate_caption", generate_caption)

builder.add_edge(START , "generate_keywords")
builder.add_edge(START, "generate_caption")

builder.add_edge("generate_caption",END)
builder.add_edge("generate_keywords",END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"topic" : " Transformer The revoluation in AI"})
    print("\n\n ==============KEYWORDS================= ")
    print(result["keywords"])
    print("\n\n ==============CAPTION================= ")
    print(result["caption"])