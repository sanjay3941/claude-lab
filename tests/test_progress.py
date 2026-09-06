from progress import (
    record_practice_result,
    load_progress,
    get_weak_topics,
)

result = record_practice_result(
    topic="deadlock",
    correct=4,
    total=5,
)

print("Recorded result:")
print(result)

print("\nFull progress:")
print(load_progress())

print("\nWeak topics:")
record_practice_result(
    topic="synchronization",
    correct=2,
    total=5,
)
print(get_weak_topics())