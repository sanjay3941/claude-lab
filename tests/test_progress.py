from progress import get_weak_topics, load_progress, record_practice_result


def test_record_practice_result_and_get_learning_progress(tmp_path, monkeypatch):
    progress_file = tmp_path / "progress.json"
    monkeypatch.setattr("progress.PROGRESS_FILE", progress_file)

    first = record_practice_result(topic="deadlock", correct=4, total=5)
    second = record_practice_result(topic="deadlock", correct=3, total=5)

    assert first == {"attempts": 1, "correct": 4, "total": 5}
    assert second == {"attempts": 2, "correct": 7, "total": 10}

    saved = load_progress()
    assert saved == {
        "topics": {"deadlock": {"attempts": 2, "correct": 7, "total": 10}}
    }


def test_get_weak_topics_respects_threshold_and_sort_order(tmp_path, monkeypatch):
    progress_file = tmp_path / "progress.json"
    monkeypatch.setattr("progress.PROGRESS_FILE", progress_file)

    record_practice_result(topic="deadlock", correct=2, total=5)  # 40.0
    record_practice_result(topic="threads", correct=4, total=5)  # 80.0
    record_practice_result(topic="synchronization", correct=3, total=5)  # 60.0

    weak_topics = get_weak_topics(threshold=70.0)

    assert [item["topic"] for item in weak_topics] == ["deadlock", "synchronization"]
    assert [item["accuracy"] for item in weak_topics] == [40.0, 60.0]


def test_load_progress_returns_default_for_invalid_json(tmp_path, monkeypatch):
    progress_file = tmp_path / "progress.json"
    progress_file.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr("progress.PROGRESS_FILE", progress_file)

    assert load_progress() == {"topics": {}}


def test_load_progress_sanitizes_invalid_topic_entries(tmp_path, monkeypatch):
    progress_file = tmp_path / "progress.json"
    progress_file.write_text(
        (
            '{"topics":{"valid":{"attempts":2,"correct":1,"total":2},'
            '"bad_type":"wrong","negative":{"attempts":-1,"correct":0,"total":1},'
            '"bad_ratio":{"attempts":1,"correct":3,"total":2}}}'
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("progress.PROGRESS_FILE", progress_file)

    assert load_progress() == {
        "topics": {"valid": {"attempts": 2, "correct": 1, "total": 2}}
    }