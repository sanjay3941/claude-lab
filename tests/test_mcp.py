import asyncio

from fastmcp import Client


async def main():
    async with Client("http://localhost:8000/mcp") as client:

        tools = await client.list_tools()

        print("Available tools:")
        for tool in tools:
            print(f" - {tool.name}")

        print("\n--- search_knowledge ---")

        result = await client.call_tool(
            "search_knowledge",
            {"query": "deadlock conditions"}
        )

        print(result.data)

        print("\n--- get_topic_content ---")

        result = await client.call_tool(
            "get_topic_content",
            {"topic": "deadlock"}
        )

        print(result.data)
        print("\n--- record_practice ---")

        result = await client.call_tool(
            "record_practice",
            {
                "topic": "deadlock",
                "correct": 4,
                "total": 5,
            }
        )

        print(result.data)
        print("\n--- get_progress ---")

        result = await client.call_tool(
            "get_progress",
            {}
        )

        print(result.data)
        print("\n--- get_weak_topics ---")

        result = await client.call_tool(
            "get_weak_topics",
            {}
        )

        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())