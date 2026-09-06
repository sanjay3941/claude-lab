import os
from json import JSONDecodeError

from starlette.requests import Request
from starlette.responses import JSONResponse

from learning import recommend_next_topic
from progress import (
    record_practice_result as save_practice_result,
    get_weak_topics,
    get_learning_progress,
)
from fastmcp import FastMCP
from knowledge import load_documents
from retrieval import retrieve_topic_content, retrieve_relevant_chunks

SERVER_INSTRUCTIONS = """
You are Claude Lab, a course-grounded learning assistant.

Learning and factual questions:
- Use get_topic_content when the student wants to learn, review, or be taught
  a topic. Ground the explanation in the retrieved course material and clearly
  distinguish that material from general knowledge.
- Use search_knowledge for focused factual questions about the student's study
  materials.

Practice:
- When the student asks to practice or requests practice questions, first call
  get_topic_content for the requested topic.
- Use the retrieved material as the primary source. Generate and evaluate
  questions yourself; the MCP server does not call an LLM.
- Do not claim course support for a question unless the retrieved material
  supports it. Ask questions interactively when appropriate.

Progress and recording:
- After a completed practice session, use record_practice only when the
  student's actual correct and total results are known. Never invent, estimate,
  or assume a score.
- Use get_progress for current performance questions and never invent progress
  data.
- Use get_learning_recommendation for next-study, next-practice, or weak-topic
  questions. Base the response on the progress returned by the tool.

Workflow and grounding:
- Call tools sequentially when genuinely required, for example:
  get_topic_content -> teach or practice -> record_practice ->
  get_learning_recommendation.
- Use the smallest number of tools necessary and do not repeat a tool call when
  the requested information is already available.
- Never fabricate course content, progress, practice history, or sources. If
  the knowledge base is insufficient, say so plainly.
"""

mcp = FastMCP("Claude Lab", instructions=SERVER_INSTRUCTIONS)


def _api_response(payload: dict, status_code: int = 200) -> JSONResponse:
    """Return a browser-friendly response for the Student Lab API."""
    response = JSONResponse(payload, status_code=status_code)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _recommendation_payload() -> dict:
    """Build structured recommendation data from the existing learning logic."""
    progress = get_learning_progress()
    if not progress:
        return {
            "available": False,
            "weak_topics": [],
            "recommendation": None,
        }

    recommendation = recommend_next_topic(progress)
    return {
        "available": True,
        "weak_topics": get_weak_topics(),
        "recommendation": recommendation,
    }


@mcp.custom_route("/api/progress", methods=["GET"])
async def api_progress(_: Request) -> JSONResponse:
    return _api_response({"progress": get_learning_progress()})


@mcp.custom_route("/api/recommendation", methods=["GET"])
async def api_recommendation(_: Request) -> JSONResponse:
    return _api_response(_recommendation_payload())


@mcp.custom_route("/api/topic/{topic:path}", methods=["GET"])
async def api_topic(request: Request) -> JSONResponse:
    topic = request.path_params["topic"].strip()
    if not topic:
        return _api_response({"error": "A topic is required."}, 400)

    documents = load_documents()
    results = retrieve_topic_content(topic=topic, documents=documents, top_k=8)
    return _api_response(
        {
            "topic": topic,
            "found": bool(results),
            "content": results,
        }
    )


@mcp.custom_route("/api/practice", methods=["POST", "OPTIONS"])
async def api_practice(request: Request) -> JSONResponse:
    if request.method == "OPTIONS":
        return _api_response({})

    try:
        payload = await request.json()
    except JSONDecodeError:
        return _api_response({"error": "Request body must be valid JSON."}, 400)

    topic = payload.get("topic")
    correct = payload.get("correct")
    total = payload.get("total")
    if (
        not isinstance(topic, str)
        or not topic.strip()
        or not isinstance(correct, int)
        or isinstance(correct, bool)
        or not isinstance(total, int)
        or isinstance(total, bool)
    ):
        return _api_response(
            {"error": "topic, correct, and total must be valid values."},
            400,
        )

    if total <= 0:
        return _api_response({"error": "Total questions must be greater than 0."}, 400)
    if correct < 0 or correct > total:
        return _api_response(
            {"error": "Correct answers must be between 0 and total."},
            400,
        )

    result = save_practice_result(topic=topic.strip(), correct=correct, total=total)
    return _api_response(
        {
            "message": f"Practice result recorded for {topic.strip()}.",
            "latest": {"correct": correct, "total": total},
            "topic_progress": {
                **result,
                "accuracy": round((result["correct"] / result["total"]) * 100, 1),
            },
        },
        201,
    )


@mcp.tool
def search_knowledge(query: str) -> str:
    """
    Search the student's study materials for a focused factual question.
    Call this tool before answering when the student asks for an answer based on
    their materials or mentions "my study materials," "my notes," "my course
    material," or similar. Treat the returned content as the source of truth for
    the student's materials; do not rely solely on general model knowledge.
    """
    print(f"[TOOL] search_knowledge query={query}")

    documents = load_documents()

    results = retrieve_relevant_chunks(
        query=query,
        documents=documents,
        top_k=5,
    )

    if not results:
        return f"No relevant results found for: {query}"

    output = []

    for result in results:
        output.append(
            f"\n[{result['source']} "
            f"- Chunk {result['chunk']} "
            f"| relevance={result['score']}]\n"
            f"{result['text']}"
        )

    return "\n".join(output)


@mcp.tool
def get_topic_content(topic: str) -> str:
    """
    Retrieve broader context from the student's study materials for a topic.
    Use this tool when the student wants to learn, review, understand, or
    practice a topic using their materials. Use the returned material as the
    basis for explanations and practice questions.
    Use search_knowledge for focused factual questions; use this tool for
    broader learning, review, and explanation of a topic.
    """
    print(f"[TOOL] get_topic_content topic={topic}")

    documents = load_documents()

    results = retrieve_topic_content(
        topic=topic,
        documents=documents,
        top_k=8,
    )

    if not results:
        return f"No study material found for topic: {topic}"

    output = []

    for result in results:
        output.append(
            f"\n[{result['source']} "
            f"- Chunk {result['chunk']} "
            f"| relevance={result['score']}]\n"
            f"{result['text']}"
        )

    return "\n".join(output)


@mcp.tool
def record_practice(
    topic: str,
    correct: int,
    total: int,
) -> str:
    """
    Record the result of a completed practice session.
    Use this tool when the student provides a score or result and asks Claude to
    record it. Do not invent or assume a score.
    """
    print(
        f"[TOOL] record_practice "
        f"topic={topic} correct={correct} total={total}"
    )

    if total <= 0:
        return "Total questions must be greater than 0."

    if correct < 0 or correct > total:
        return "Correct answers must be between 0 and total."

    result = save_practice_result(
        topic=topic,
        correct=correct,
        total=total,
    )

    accuracy = (
        result["correct"] / result["total"]
    ) * 100

    return (
        f"Practice result recorded for {topic}.\n"
        f"Latest session: {correct}/{total}\n"
        f"Overall accuracy: {accuracy:.1f}%\n"
        f"Total attempts: {result['attempts']}"
    )

@mcp.tool
def get_progress() -> str:
    """
    Retrieve the student's accumulated practice performance.
    Use this tool when the student asks about their progress, performance, or
    accuracy.
    """
    print("[TOOL] get_progress")

    progress = get_learning_progress()

    if not progress:
        return "No practice progress recorded yet."

    output = ["Learning Progress"]

    for topic, data in progress.items():

        output.append(
            f"\nTopic: {topic}\n"
            f"Attempts: {data['attempts']}\n"
            f"Correct: {data['correct']}/{data['total']}\n"
            f"Accuracy: {data['accuracy']}%"
        )

    return "\n".join(output)


@mcp.tool
def get_learning_recommendation() -> str:
    """
    Use this tool when the student asks which topics are weak or what they
    should study or practice next. The recommendation is based on recorded
    practice history. Do not invent or assume progress data.
    """
    print("[TOOL] get_learning_recommendation")

    progress = get_learning_progress()

    if not progress:
        return (
            "There is not enough practice data to make a learning "
            "recommendation."
        )

    weak_topics = sorted(
        (
            (topic, data["accuracy"])
            for topic, data in progress.items()
            if data["accuracy"] < 70
        ),
        key=lambda item: (item[1], item[0]),
    )
    recommendation = recommend_next_topic(progress)
    strategy = recommendation["strategy"]

    if weak_topics:
        weak_output = "\n".join(
            f"- {topic}: {accuracy}%"
            for topic, accuracy in weak_topics
        )
    else:
        weak_output = "None"

    return (
        f"Weak topics:\n{weak_output}\n\n"
        f"Recommended topic: {recommendation['topic']}\n"
        f"Current accuracy: {recommendation['accuracy']}%\n"
        f"Recommended level: {strategy['level']}\n"
        f"Questions: {strategy['questions']}\n"
        f"Difficulty: {strategy['difficulty']}\n"
        f"Focus: {strategy['focus']}"
    )
if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    mcp.run(
        transport="http",
        host=host,
        port=port,
    )