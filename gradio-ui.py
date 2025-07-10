import gradio as gr
import requests
import ast
import json
API_URL = "http://localhost:8000/chat"

session_id = ""
def format_response(text):
    if isinstance(text, list):
        return "\n".join(f"- `{item}`" for item in text)

    if isinstance(text, dict):
        return "\n".join(f"- **{k}**: `{v}`" for k, v in text.items())

    # Handle stringified list or dict
    if isinstance(text, str):
        try:
            obj = ast.literal_eval(text)
            if isinstance(obj, list):
                return "\n".join(f"- `{item}`" for item in obj)
            elif isinstance(obj, dict):
                return "\n".join(f"- **{k}**: `{v}`" for k, v in obj.items())
        except:
            pass

    # Multi-line string? Format cleanly
    if "\n" in text:
        return f"```\n{text}\n```"

    return text

def chat_fn(message, history):
    global session_id
    payload = {
        "user_input": message,
        "session_id": session_id  # send as string, not list
    }
    response = requests.post(API_URL, json=payload).json()
    session_id = response.get("session_id", session_id)
    formatted = format_response(response["response"])
    return formatted

gr.ChatInterface(fn=chat_fn).launch()
