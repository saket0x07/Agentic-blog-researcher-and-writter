from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator

# --- Pydantic Schemas for Structured LLM Outputs ---

class EvidenceItem(BaseModel):
    title: str = Field(description="The title of the source page.")
    url: str = Field(description="The URL of the source page.")
    snippet: str = Field(description="A short relevant excerpt from the page.")
    date: str = Field(description="The publication or crawl date of the source.")

class TaskObject(BaseModel):
    id: str = Field(description="A unique short identifier for the section, e.g., 'sec_1'")
    title: str = Field(description="The title of the blog section.")
    goal: str = Field(description="The main goal and thesis of this section.")
    bullet_points: List[str] = Field(description="Specific concepts, points, or evidence to cover in this section.")
    target_word_count: int = Field(description="Target length for this section in words.")
    requires_citations: bool = Field(default=False, description="Whether this section must cite URLs from the evidence pack.")
    requires_code_blocks: bool = Field(default=False, description="Whether this section needs technical code block examples.")

class PlanObject(BaseModel):
    title: str = Field(description="The overall title of the blog.")
    audience: str = Field(description="The target audience for the blog post.")
    tone: str = Field(description="The writing style or tone (e.g., technical, conversational).")
    tasks: List[TaskObject] = Field(description="A ordered list of section tasks defining the structure of the blog.")

class SectionDraft(BaseModel):
    task_id: str = Field(description="The ID of the task this draft corresponds to.")
    title: str = Field(description="The title of the section.")
    content: str = Field(description="The drafted markdown content for the section.")

# --- Graph State definitions ---

class OverallState(TypedDict):
    topic: str                                     # Initial blog topic/prompt
    knowledge_category: str                        # "closed_book", "open_book", or "hybrid"
    search_queries: List[str]                      # Tavily search queries generated
    evidence: List[Dict[str, Any]]                 # Collected search results (Evidence Pack)
    plan: Dict[str, Any]                           # The Orchestrator's plan (matches PlanObject structure)
    section_drafts: Annotated[List[Dict[str, Any]], operator.add] # Section inputs gathered from Worker Nodes
    final_blog: str                                # The finalized blog markdown text
    images: List[str]                              # List of generated local image paths
    image_prompts: List[Dict[str, Any]]  
    image_choices: List[Dict[str, Any]]            # User-selected interactive image options (mode, prompt, caption, section_id)

