import re


CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


def tokenize(text: str) -> list[str]:
    """Convert text into searchable terms."""
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def create_chunks(text: str) -> list[str]:
    """Split text into meaningful paragraph-based chunks."""

    text = text.strip()

    if not text:
        return []

    # Normalize excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        # If adding the paragraph stays within the target size,
        # keep it in the current chunk.
        if len(current_chunk) + len(paragraph) + 2 <= CHUNK_SIZE:

            if current_chunk:
                current_chunk += "\n\n"

            current_chunk += paragraph

        else:

            if current_chunk:
                chunks.append(current_chunk)

            # Very large paragraphs are split separately.
            if len(paragraph) > CHUNK_SIZE:

                start = 0

                while start < len(paragraph):

                    end = start + CHUNK_SIZE

                    chunk = paragraph[start:end].strip()

                    if chunk:
                        chunks.append(chunk)

                    start = end

            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def score_text(query: str, text: str) -> int:
    """Calculate a simple relevance score."""

    query_terms = tokenize(query)
    text_lower = text.lower()

    score = 0

    for term in query_terms:
        occurrences = text_lower.count(term)

        if len(term) >= 6:
            score += occurrences * 2
        else:
            score += occurrences

    if query.lower() in text_lower:
        score += 5

    return score


def retrieve_relevant_chunks(
    query: str,
    documents: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """Return the highest-scoring chunks from the documents."""

    results = []

    for document in documents:

        chunks = create_chunks(document["text"])

        for chunk_number, chunk in enumerate(chunks, start=1):

            score = score_text(query, chunk)

            if score > 0:
                results.append(
                    {
                        "score": score,
                        "source": document["source"],
                        "chunk": chunk_number,
                        "text": chunk,
                    }
                )

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return results[:top_k]

def retrieve_topic_content(
    topic: str,
    documents: list[dict],
    top_k: int = 8,
) -> list[dict]:
    """Retrieve a broader set of chunks for studying a topic."""

    return retrieve_relevant_chunks(
        query=topic,
        documents=documents,
        top_k=top_k,
    )