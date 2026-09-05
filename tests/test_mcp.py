import asyncio

from fastmcp import Client


async def main():
    async with Client("http://localhost:8000/mcp") as client:

        tools = await client.list_tools()

        print("Available tools:")
        for tool in tools:
            print(f" - {tool.name}")

        result = await client.call_tool(
            "search_knowledge",
            {"query": "deadlock"}
        )

        print("\nTool result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())