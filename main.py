# mcp_server.py
from fastapi import FastAPI, Request
from langgraph_agent import init_graph, build_initial_state
from uuid import uuid4

app = FastAPI()
workflow = init_graph()
session_store = {}

@app.get("/")
def root():
    return {"message": "MCP Server is running!"}

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        print("Incoming request body:", body)

        message = body.get("user_input") or body.get("message") or ""
        session_id = str(body.get("session_id", "")).strip()

        # Assign new session ID if invalid or default
        if not session_id or session_id.lower() in {"none", "null", "undefined", "default"}:
            session_id = str(uuid4())

        if not message:
            return {"response": "Please provide a message.", "session_id": session_id}

        if session_id not in session_store or not isinstance(session_store.get(session_id), dict):
            session_store[session_id] = build_initial_state(message, session_id)
        else:
            session_store[session_id]["messages"].append({"role": "user", "content": message})

        state = workflow.invoke(session_store[session_id])
        session_store[session_id] = state

        reply = next((m["content"] for m in reversed(state["messages"]) if m["role"] == "assistant"), "")

        return {"response": reply, "session_id": session_id}

    except Exception as e:
        import traceback
        print("Exception in /chat:", traceback.format_exc())
        return {"response": f"❌ Internal Server Error: {str(e)}", "session_id": "default"}
