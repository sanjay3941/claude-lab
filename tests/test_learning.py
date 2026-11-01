from learning import get_practice_strategy, recommend_next_topic


def test_recommend_next_topic_selects_lowest_accuracy():
    progress = {
        "operating systems": {"accuracy": 80},
        "deadlocks": {"accuracy": 40},
        "computer networks": {"accuracy": 65},
    }

    result = recommend_next_topic(progress)

    assert result["topic"] == "deadlocks"
    assert result["accuracy"] == progress["deadlocks"]["accuracy"]
    assert result["strategy"] == get_practice_strategy(result["accuracy"])


def test_recommend_next_topic_empty_progress():
    result = recommend_next_topic({})

    assert result["topic"] is None
    assert result["strategy"] is None


def test_recommend_next_topic_with_multiple_topics():
    progress = {
        "deadlock": {"accuracy": 40.0},
        "threads": {"accuracy": 80.0},
        "synchronization": {"accuracy": 60.0},
    }

    result = recommend_next_topic(progress)

    assert result["topic"] == "deadlock"
    assert result["accuracy"] == 40.0
    assert result["strategy"]["level"] == "foundational"
    assert result["strategy"]["difficulty"] == "easy"
    assert result["strategy"]["questions"] == 5


def test_get_practice_strategy_buckets():
    assert get_practice_strategy(40)["level"] == "foundational"
    assert get_practice_strategy(60)["level"] == "targeted"
    assert get_practice_strategy(80)["level"] == "mixed"
    assert get_practice_strategy(90)["level"] == "advanced"