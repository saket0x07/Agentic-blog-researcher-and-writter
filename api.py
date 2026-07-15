import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from langchain_core.callbacks import BaseCallbackHandler

from blog_agent.graph.workflow import blog_agent_graph

class TokenUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.cost_usd = 0.0

    def on_llm_end(self, response, **kwargs):
        try:
            for generations in response.generations:
                for gen in generations:
                    message = getattr(gen, "message", None)
                    if message and hasattr(message, "response_metadata"):
                        metadata = message.response_metadata
                        token_usage = metadata.get("token_usage")
                        if token_usage:
                            p_tok = token_usage.get("prompt_tokens", 0)
                            c_tok = token_usage.get("completion_tokens", 0)
                            t_tok = token_usage.get("total_tokens", 0)
                            
                            self.prompt_tokens += p_tok
                            self.completion_tokens += c_tok
                            self.total_tokens += t_tok
                            
                            model_name = metadata.get("model_name", "").lower()
                            if "gpt-4o-mini" in model_name:
                                self.cost_usd += (p_tok * 0.150 / 1_000_000) + (c_tok * 0.600 / 1_000_000)
                            elif "nemotron" in model_name:
                                self.cost_usd += 0.0
                            else:
                                self.cost_usd += (t_tok / 1000) * 0.0015
        except Exception:
            pass

app = FastAPI(
    title="FX LangGraph API",
    description="API for the LangGraph-based Blog Agent",
    version="1.0.0"
)

class BlogWriteRequest(BaseModel):
    topic: str

class BlogRequest(BaseModel):
    topic: str

class BlogResponse(BaseModel):
    status: str
    final_blog: Optional[str] = None
    raw_state: Optional[Dict[str, Any]] = None

@app.get("/")
def read_root():
    return {"status": "ok", "service": "FX LangGraph API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/blog/write")
def write_blog(request: BlogWriteRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    try:
        result = blog_agent_graph.invoke({"topic": request.topic})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    final_blog = result.get("final_blog", "") or ""
    plan = result.get("plan") or {}
    file_path = result.get("file_path")

    return {
        "status": "completed",
        "topic": request.topic,
        "title": plan.get("title"),
        "file_path": file_path,
        "word_count": len(final_blog.split()) if final_blog else 0,
        "preview": final_blog[:2000] if final_blog else "",
    }

@app.post("/generate", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """
    Synchronously generates a blog using the LangGraph workflow.
    Provides compatibility with the Agent-Harness BlogWriterAPIAdapter.
    """
    try:
        print(f"\n[API] Received request to generate blog on: '{request.topic}'")
        graph_inputs = {"topic": request.topic}
        
        # Stream updates from the graph and print node progress to console
        final_state = {}
        node_traces = {}
        
        callback_handler = TokenUsageCallbackHandler()
        config_dict = {"callbacks": [callback_handler]}
        
        prev_p_tokens = 0
        prev_c_tokens = 0
        prev_t_tokens = 0
        prev_cost = 0.0
        
        # Create stream generator
        stream_generator = blog_agent_graph.stream(graph_inputs, config=config_dict, stream_mode="updates")
        
        while True:
            try:
                event = next(stream_generator)
                
                # Calculate tokens/cost delta for this step
                p_delta = callback_handler.prompt_tokens - prev_p_tokens
                c_delta = callback_handler.completion_tokens - prev_c_tokens
                t_delta = callback_handler.total_tokens - prev_t_tokens
                cost_delta = callback_handler.cost_usd - prev_cost
                
                # Update previous counters
                prev_p_tokens = callback_handler.prompt_tokens
                prev_c_tokens = callback_handler.completion_tokens
                prev_t_tokens = callback_handler.total_tokens
                prev_cost = callback_handler.cost_usd
                
                for node_name, output in event.items():
                    print(f"   [API Node] {node_name} completed.")
                    
                    # Prevent overwriting when node_name is identical (e.g. worker runs)
                    unique_node_name = node_name
                    counter = 1
                    while unique_node_name in node_traces:
                        unique_node_name = f"{node_name}_{counter}"
                        counter += 1
                    
                    node_traces[unique_node_name] = {
                        "prompt_tokens": p_delta,
                        "completion_tokens": c_delta,
                        "total_tokens": t_delta,
                        "cost_usd": cost_delta
                    }
                    
                    # Accumulate state updates
                    for k, v in output.items():
                        if k == "section_drafts":
                            if "section_drafts" not in final_state:
                                final_state["section_drafts"] = []
                            final_state["section_drafts"].extend(v)
                        else:
                            final_state[k] = v
            except StopIteration:
                break
                
        final_state["topic"] = request.topic
        final_state["node_traces"] = node_traces
        blog_content = final_state.get("final_blog") or final_state.get("final_blog_content")
        
        print("   [API] Generation completed successfully!")
        return BlogResponse(
            status="success",
            final_blog=blog_content,
            raw_state=final_state
        )
    except Exception as e:
        print(f"[API Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))
