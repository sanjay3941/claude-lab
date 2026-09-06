import os
from progress import (
    record_practice_result as save_practice_result,
    get_learning_progress,
    get_weak_topics as find_weak_topics,
)
from fastmcp import FastMCP
from knowledge import load_documents
from retrieval import retrieve_topic_content, retrieve_relevant_chunks

mcp = FastMCP("Claude Lab")


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
def get_weak_topics() -> str:
    """
    Identify topics where the student's accuracy is below 70%.
    Use this tool when the student asks what to study next, where they are weak,
    or what needs more practice.
    """
    print("[TOOL] get_weak_topics")

    weak_topics = find_weak_topics()

    if not weak_topics:
        return "No weak topics identified."

    output = ["Topics needing more practice:"]

    for topic in weak_topics:
        output.append(
            f"\nTopic: {topic['topic']}\n"
            f"Accuracy: {topic['accuracy']}%\n"
            f"Attempts: {topic['attempts']}\n"
            f"Correct: {topic['correct']}/{topic['total']}"
        )

    return "\n".join(output)
if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    mcp.run(
        transport="http",
        host=host,
        port=port,
    )