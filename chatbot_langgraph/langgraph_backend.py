import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Define the state shape
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the LLM (using OpenRouter as configured in .env)
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    chatbot_llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="nvidia/nemotron-3-super-120b-a12b"
    )
else:
    # Fallback to OpenAI if no OpenRouter key is configured
    chatbot_llm = ChatOpenAI(model="gpt-4o-mini")

# Define the chatbot node function
def chatbot_node(state: State):
    response = chatbot_llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the LangGraph workflow
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Set up checkpointer memory
memory = MemorySaver()

# Compile the graph
chatbot = builder.compile(checkpointer=memory)
