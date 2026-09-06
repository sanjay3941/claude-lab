from pathlib import Path

import pymupdf

from retrieval import retrieve_relevant_chunks


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def load_documents() -> list[dict]:
    """Load all supported study documents."""

    documents = []

    # Load PDF documents
    for pdf_path in KNOWLEDGE_DIR.rglob("*.pdf"):
        try:
            with pymupdf.open(pdf_path) as document:

                for page_number, page in enumerate(document):

                    text = page.get_text()

                    if text.strip():
                        documents.append(
                            {
                                "source": (
                                    f"{pdf_path.name} "
                                    f"- Page {page_number + 1}"
                                ),
                                "text": text,
                            }
                        )

        except Exception as error:

            print(
                f"Error reading {pdf_path.name}: {error}"
            )

    # Load TXT documents
    for text_path in KNOWLEDGE_DIR.rglob("*.txt"):
        try:

            text = text_path.read_text(
                encoding="utf-8"
            )

            if text.strip():
                documents.append(
                    {
                        "source": text_path.name,
                        "text": text,
                    }
                )

        except Exception as error:

            print(
                f"Error reading {text_path.name}: {error}"
            )

    return documents


def search_local_knowledge(query: str) -> str:
    """Search study materials and return relevant chunks."""

    query = query.strip()

    if not query:
        return "Please provide a search query."

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