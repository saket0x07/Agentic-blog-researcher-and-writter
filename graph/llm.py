import os
from langchain_openai import ChatOpenAI
from blog_agent import config

def get_llm() -> ChatOpenAI:
    """
    Initialize and return the LLM client (GPT-4o mini) based on env configurations.
    Prefers OpenRouter if configured, otherwise falls back to standard OpenAI.
    """
    if config.OPENROUTER_API_KEY:
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
            model="openai/gpt-4o-mini"
        )
    elif config.OPENAI_API_KEY:
        return ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4o-mini"
        )
    else:
        # If neither is set, let it raise or default to OpenAI (so LangChain can read system environment)
        return ChatOpenAI(model="gpt-4o-mini")
