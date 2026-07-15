from dotenv import load_dotenv
import os
from typing import TypedDict

from langgraph.graph import StateGraph , START , END
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    base_url="https://openrouter.ai/api/v1",
    # google/gemma-4-26b-a4b-it:free
    api_key=OPENROUTER_API_KEY,
    temperature=0.7,
    
)


class BlogState(TypedDict):
    topic:str
    draft:str
    final_post:str


def generate_draft(state: BlogState):
    prompt = f"""
You are an expert content writer.
Write a blog post outline for the following topic:
{state['topic']}
"""

    response = llm.invoke(prompt)
    return {"draft" : response.content}


def curate_content(state: BlogState):
    prompt = f"""
You are an expert content writer.
Curate the content for the following topic and the generated draft:
Topic: {state['topic']}
Draft: {state['draft']}
Add relevant information and make it engaging.
"""

    response = llm.invoke(prompt)
    return {"final_post" : response.content}


build = StateGraph(BlogState)

build.add_node("generate_draft", generate_draft)
build.add_node("curate_content", curate_content)

build.add_edge(START , "generate_draft")
build.add_edge("generate_draft", "curate_content")
build.add_edge("curate_content", END)

graph = build.compile()

if __name__ == "__main__":
    result = graph.invoke({"topic" : " Transformer The revoluation in AI"})
    print("\n\n ==============DRAFT================= ")
    print(result["draft"])
    print("\n\n ==============FINAL_POST================= ")
    print(result["final_post"])

    
    