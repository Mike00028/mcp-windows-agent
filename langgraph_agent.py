from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict
import requests
import json
from tools.windows_service import is_service_running, start_service, stop_service
from tools.file_search import find_file as raw_find_file
from tools.registry_tool import get_registry_value, set_registry_value

# Wrapper to return top 3 results only
def find_file(filename: str, search_path: Optional[str] = "C:\\Users\\santo") -> list:
    results = raw_find_file(filename, search_path)
    return results[:10] if isinstance(results, list) else results

# Tool registry
tool_registry = {
    "is_service_running": is_service_running,
    "start_service": start_service,
    "stop_service": stop_service,
    "find_file": find_file,
    "get_registry_value": get_registry_value,
    "set_registry_value": set_registry_value
}

# Agent state structure
class AgentState(TypedDict):
    messages: List[dict]
    pending_function: Optional[str]
    collected_params: Dict[str, str]
    missing_params: List[str]
    session_id: str
    retry_count: int
    function: Optional[str]
    parameters: Optional[Dict[str, str]]

# Call LLM and expect JSON response
def call_llama(messages: List[Dict]) -> Dict:
    limited_messages = messages[-4:] if len(messages) >= 4 else messages

    prompt = """
You are a system assistant that responds in structured JSON only. Here are valid responses:
1. If the user requests an action, respond like:
{
  "function": "start_service",
  "parameters": {
    "service_name": "<required service name>"
  }
}
2. If you can't identify the function, return:
{ "content": "I could not understand your request." }

Available functions:
- is_service_running {"service_name": str}
- start_service {"service_name": str}
- stop_service {"service_name": str}
- find_file {"filename": str, "search_path": Optional[str]}
- get_registry_value {"key": str, "hive": str}
- set_registry_value {"key": str, "hive": str, "value": str}
""" + "\n" + "\n".join([f"{m['role']}: {m['content']}" for m in limited_messages]) + "\nassistant:"

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False}
    )

    result = response.json()
    output = result.get("response", "").strip()

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"content": output}

def is_chitchat(message: str) -> bool:
    check_msg = (
        "Classify this input as 'yes' if it's a greeting, small talk, or irrelevant to system operations. "
        "Otherwise respond 'no'. Return JSON as: {\"classification\":\"yes\"} or {\"classification\":\"no\"}."
    )
    response = call_llama([{"role": "user", "content": check_msg + "\n" + message}])
    try:
        result = json.loads(response.get("content", ""))
        return result.get("classification", "").lower() == "yes"
    except:
        return False

def check_chitchat(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1]["content"].strip()
    if is_chitchat(last_msg):
        state["messages"].append({
            "role": "assistant",
            "content": "Got it! Let me know if you need help with system tasks."
        })
        state["pending_function"] = "__end__"
    else:
        state["pending_function"] = None
    return state

def is_missing(value: str) -> bool:
    return (
        value is None
        or str(value).strip() == ""
        or str(value).lower() in {"none", "null"}
        or "<" in str(value)
    )

def extract_function(state: AgentState):
    llm_response = call_llama(state["messages"])

    if "function" in llm_response:
        name = llm_response["function"]
        args = llm_response.get("parameters", {})
        missing = [k for k, v in args.items() if is_missing(v)]

        if missing:
            state.update({
                "pending_function": name,
                "collected_params": args,
                "missing_params": missing,
                "retry_count": 0
            })
            state["messages"].append({
                "role": "assistant",
                "content": f"Please provide: {', '.join(missing)}"
            })
        else:
            return {
                **state,
                "function": name,
                "parameters": args,
                "pending_function": name,
                "collected_params": args,
                "missing_params": [],
                "retry_count": 0
            }
    else:
        state["messages"].append({
            "role": "assistant",
            "content": llm_response.get("content", "Sorry, I didn't understand.")
        })
        state["pending_function"] = "__end__"

    return state

def fill_missing_param(state: AgentState):
    llm_response = call_llama(state["messages"])
    state["collected_params"].update(llm_response.get("parameters", {}))

    still_missing = [
        k for k in state["missing_params"]
        if k not in state["collected_params"] or is_missing(state["collected_params"][k])
    ]

    if not still_missing:
        return {
            **state,
            "function": state["pending_function"],
            "parameters": state["collected_params"],
            "missing_params": [],
            "retry_count": 0
        }

    state["missing_params"] = still_missing
    state["retry_count"] += 1

    if state["retry_count"] >= 1:
        state["messages"].append({
            "role": "assistant",
            "content": f"I'm sorry, I still don't have enough information to continue. Missing parameters: {', '.join(still_missing)}."
        })
        state["pending_function"] = "__end__"
        return state

    state["messages"].append({
        "role": "assistant",
        "content": f"Still need: {', '.join(still_missing)}"
    })
    return state

def call_tool(state: AgentState):
    try:
        fn = state["function"]
        params = state["parameters"]
        tool = tool_registry.get(fn)
        if not tool:
            raise ValueError(f"Unknown tool: {fn}")
        result = tool(**params)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        result = f"Error: {e}\nTraceback:\n{tb}"
    state["messages"].append({"role": "assistant", "content": str(result)})
    return state

def router(state):
    try:
        if state.get("pending_function") == "__end__":
            return END
        if not state.get("pending_function"):
            return "extract"
        if state.get("missing_params"):
            if state.get("retry_count", 0) >= 3:
                return END
            return "ask_param"
        return "call_tool"
    except Exception as e:
        state["messages"].append({
            "role": "assistant",
            "content": f"Routing error: {str(e)}"
        })
        return END

def init_graph():
    graph = StateGraph(AgentState)
    graph.add_node("check_chitchat", check_chitchat)
    graph.add_node("extract", extract_function)
    graph.add_node("ask_param", fill_missing_param)
    graph.add_node("call_tool", call_tool)

    graph.set_entry_point("check_chitchat")
    graph.add_conditional_edges("check_chitchat", lambda s: END if s.get("pending_function") == "__end__" else "extract", {
        "extract": "extract",
        END: END
    })
    graph.add_conditional_edges("extract", router, {
        "call_tool": "call_tool",
        "ask_param": "ask_param",
        "extract": "extract",
        END: END
    })
    graph.add_conditional_edges("ask_param", router, {
        "call_tool": "call_tool",
        "ask_param": "ask_param",
        END: END
    })
    graph.add_edge("call_tool", END)
    return graph.compile()

def build_initial_state(user_input: str, session_id: str) -> AgentState:
    return {
        "messages": [{"role": "user", "content": user_input}],
        "pending_function": None,
        "collected_params": {},
        "missing_params": [],
        "session_id": session_id,
        "retry_count": 0,
        "function": None,
        "parameters": {}
    }
