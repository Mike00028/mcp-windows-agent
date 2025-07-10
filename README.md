#LangGraph MCP Server

## Overview
This project is a modular, agent-based system for automating Windows system administration and file operations using natural language commands. It leverages LangGraph (and optionally LangChain) to orchestrate tool-based agents, enabling users to interact with Windows services, search for files, and manage the Windows registry through conversational prompts.

## Features
- **Windows Service Management**: Start, stop, and check the status of Windows services via natural language.
- **File Search**: Search for files by name within specified directories, returning the top results.
- **Windows Registry Operations**: Get and set registry values programmatically.
- **Agent Orchestration**: Uses a state machine (LangGraph) to manage agent state, handle missing parameters, and route user requests to the correct tool.
- **LLM Integration**: Integrates with an LLM (e.g., Llama 3) to interpret user intent and extract structured commands.
- **Extensible Tooling**: Easily add new tools for additional system operations or business logic.
## Screenshots

![Agent UI Example](docs/screenshot1.png)
![File Search Result](docs/screenshot2.png)
## How It Works
1. **User Input**: The user provides a natural language command (e.g., "Start the Print Spooler service").
2. **LLM Parsing**: The agent sends the message to an LLM, which returns a structured JSON response indicating the function to call and its parameters.
3. **Parameter Handling**: If required parameters are missing, the agent asks the user for clarification.
4. **Tool Invocation**: The agent dynamically invokes the appropriate tool (function) with the provided parameters.
5. **Response**: The result is returned to the user in a conversational format.

## Project Structure
- `langgraph_agent.py`: Main agent logic, state management, and orchestration.
- `tools/`
  - `windows_service.py`: Tools for managing Windows services.
  - `file_search.py`: Tools for searching files on disk.
  - `registry_tool.py`: Tools for interacting with the Windows registry.
- `main.py`, `run.py`: Entry points for running the agent or server.
- `requirements.txt`: Python dependencies.

## Example Usage
- **Start a Service**: "Start the Print Spooler service."
- **Find a File**: "Find all Excel files in my Documents folder."
- **Get Registry Value**: "What is the value of 'Path' in the system registry?"

## Setup & Installation
1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Ensure you have the required permissions to manage Windows services and registry.
5. Run the agent:
   ```sh
   python run.py
   ```

## Requirements
- Python 3.10+
- Windows OS (for service and registry tools)
- LLM API or local LLM server (e.g., Llama 3)

## Extending the Project
To add new tools, create a new Python file in the `tools/` directory, define your function, and register it in `langgraph_agent.py`.

## Gradio UI
This project includes a Gradio-based web interface (`gradio-ui.py`) for interacting with the agent. The Gradio UI allows users to:
- Enter natural language commands in a browser.
- View agent responses and results in real time.
- Use the system without needing to run Python scripts from the command line.

### How to Use the Gradio UI
1. Start the Gradio UI by running:
   ```sh
   python gradio-ui.py
   ```
2. Open the provided local URL in your web browser (usually `http://127.0.0.1:7860/`).
3. Enter your requests (e.g., "Start the Print Spooler service" or "Find all Excel files in my Documents folder").
4. View the agent's response and any results directly in the browser.

The Gradio UI makes the system accessible to non-technical users and is ideal for demos, support, or internal automation portals.

## License
This project is provided for educational and internal automation purposes. Please review and comply with your organization's IT policies before using automation tools on production systems.

---

*Professional documentation written by GitHub Copilot.*
