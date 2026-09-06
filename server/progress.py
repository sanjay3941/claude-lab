import json
from pathlib import Path


PROGRESS_FILE = Path(__file__).parent.parent / "data" / "progress.json"


def load_progress() -> dict:
    """Load learning progress from the progress file."""

    if not PROGRESS_FILE.exists():
        return {"topics": {}}

    with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_progress(progress: dict) -> None:
    """Save learning progress to the progress file."""

    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            progress,
            file,
            indent=4,
        )


def record_practice_result(
    topic: str,
    correct: int,
    total: int,
) -> dict:
    """Record a practice result for a topic."""

    progress = load_progress()

    topics = progress.setdefault("topics", {})

    if topic not in topics:
        topics[topic] = {
            "attempts": 0,
            "correct": 0,
            "total": 0,
        }

    topics[topic]["attempts"] += 1
    topics[topic]["correct"] += correct
    topics[topic]["total"] += total

    save_progress(progress)

    return topics[topic]

def get_learning_progress() -> dict:
    """Return learning progress with calculated accuracy."""

    progress = load_progress()

    topics = progress.get("topics", {})

    result = {}

    for topic, data in topics.items():

        total = data.get("total", 0)
        correct = data.get("correct", 0)

        accuracy = (
            (correct / total) * 100
            if total > 0
            else 0
        )

        result[topic] = {
            "attempts": data.get("attempts", 0),
            "correct": correct,
            "total": total,
            "accuracy": round(accuracy, 1),
        }

    return result
def get_weak_topics(threshold: float = 70.0) -> list[dict]:
    """Return topics whose accuracy is below the given threshold."""

    progress = get_learning_progress()

    weak_topics = []

    for topic, data in progress.items():

        if data["accuracy"] < threshold:
            weak_topics.append(
                {
                    "topic": topic,
                    "accuracy": data["accuracy"],
                    "attempts": data["attempts"],
                    "correct": data["correct"],
                    "total": data["total"],
                }
            )

    weak_topics.sort(
        key=lambda item: item["accuracy"]
    )

    return weak_topics