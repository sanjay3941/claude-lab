import os

from fastmcp import FastMCP
from knowledge import search_local_knowledge

mcp = FastMCP("Claude Lab")

@mcp.tool
def search_knowledge(query: str) -> str:
    """
    Search the student's study materials for relevant information.
    """
    return search_local_knowledge(query)


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    mcp.run(
        transport="http",
        host=host,
        port=port,
    )