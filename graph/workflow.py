from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from blog_agent.graph.state import OverallState
from blog_agent.graph.nodes.router import router_node
from blog_agent.graph.nodes.research import research_node
from blog_agent.graph.nodes.planner import planner_node
from blog_agent.graph.nodes.worker import worker_node
from blog_agent.graph.nodes.reducer import reducer_node

def route_after_router(state: OverallState) -> str:
    """
    Conditional routing edge after the router node.
    - If the topic is 'closed_book', we jump straight to planning (no research).
    - If the topic is 'open_book' or 'hybrid', we trigger web research.
    """
    category = state.get("knowledge_category", "hybrid")
    if category == "closed_book":
        return "planner"
    else:
        return "research"

def map_tasks_to_workers(state: OverallState) -> list[Send]:
    """
    Fan-out mechanism mapping tasks from the plan to parallel Worker writer nodes.
    """
    plan = state.get("plan")
    if not plan or "tasks" not in plan:
        print("[Workflow] Error: No plan tasks found to map to workers.")
        return []
    
    sends = []
    for task in plan["tasks"]:
        # Build the slice of state to send to each worker node
        worker_state = {
            "task": task,
            "title": plan["title"],
            "audience": plan["audience"],
            "tone": plan["tone"],
            "evidence": state.get("evidence", [])
        }
        sends.append(Send("worker", worker_state))
        
    print(f"[Workflow] Fanning out {len(sends)} tasks to parallel worker nodes...")
    return sends

def create_workflow():
    """
    Assembles the state graph, defines nodes, edges, and compiles the workflow.
    """
    # 1. Initialize StateGraph with the OverallState shape
    builder = StateGraph(OverallState)
    
    # 2. Add Nodes
    builder.add_node("router", router_node)
    builder.add_node("research", research_node)
    builder.add_node("planner", planner_node)
    builder.add_node("worker", worker_node)
    builder.add_node("reducer", reducer_node)
    
    # 3. Add Edges & Conditional Routing
    builder.add_edge(START, "router")
    
    # Router conditional edge
    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "planner": "planner",
            "research": "research"
        }
    )
    
    # Research goes to planner once done
    builder.add_edge("research", "planner")
    
    # Planner maps tasks to parallel Worker nodes (Fan-out)
    builder.add_conditional_edges(
        "planner",
        map_tasks_to_workers,
        ["worker"]
    )
    
    # Workers aggregate (Fan-in) to Reducer
    builder.add_edge("worker", "reducer")
    
    # Reducer completes the graph
    builder.add_edge("reducer", END)
    
    # Compile the graph
    graph = builder.compile()
    return graph

# Export a compiled graph instance
blog_agent_graph = create_workflow()
