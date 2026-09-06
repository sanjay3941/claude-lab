def get_practice_strategy(accuracy: float) -> dict:
    """Determine an appropriate practice strategy from accuracy."""

    if accuracy < 50:
        return {
            "level": "foundational",
            "questions": 5,
            "difficulty": "easy",
            "focus": "Review the fundamentals before attempting harder questions.",
        }

    if accuracy < 70:
        return {
            "level": "targeted",
            "questions": 5,
            "difficulty": "easy-to-medium",
            "focus": "Focus on the concepts the student is struggling with.",
        }

    if accuracy < 85:
        return {
            "level": "mixed",
            "questions": 5,
            "difficulty": "medium",
            "focus": "Mix conceptual and application-based questions.",
        }

    return {
        "level": "advanced",
        "questions": 5,
        "difficulty": "medium-to-hard",
        "focus": "Challenge the student with application and reasoning questions.",
    }


def recommend_next_topic(progress: dict) -> dict:
    """Recommend the topic with the lowest recorded accuracy."""

    if not progress:
        return {
            "topic": None,
            "reason": "No practice history is available yet.",
            "strategy": None,
        }

    topic, topic_progress = min(
        progress.items(),
        key=lambda item: item[1]["accuracy"],
    )
    accuracy = topic_progress["accuracy"]

    return {
        "topic": topic,
        "accuracy": accuracy,
        "reason": (
            f"{topic} was selected because it currently has the lowest "
            "recorded accuracy."
        ),
        "strategy": get_practice_strategy(accuracy),
    }