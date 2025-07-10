import uvicorn
import logging

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("mcp_server.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting MCP Server on http://localhost:8000")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
