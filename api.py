from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from blog_agent.graph.workflow import blog_agent_graph

app = FastAPI(title="FX LangGraph API")


class BlogWriteRequest(BaseModel):
    topic: str


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
