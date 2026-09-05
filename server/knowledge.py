from pathlib import Path

import pymupdf


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def search_local_knowledge(query: str) -> str:
    """Search study materials for pages or text containing the query."""

    query = query.lower().strip()

    if not query:
        return "Please provide a search query."

    results = []

    # Search PDF files
    for pdf_path in KNOWLEDGE_DIR.rglob("*.pdf"):
        try:
            with pymupdf.open(pdf_path) as document:
                for page_number, page in enumerate(document):
                    text = page.get_text()

                    if query in text.lower():
                        results.append(
                            f"\n[{pdf_path.name} - Page {page_number + 1}]\n"
                            f"{text[:2000]}"
                        )

        except Exception as error:
            results.append(
                f"[Error reading {pdf_path.name}: {error}]"
            )

    # Search text files
    for text_path in KNOWLEDGE_DIR.rglob("*.txt"):
        try:
            text = text_path.read_text(encoding="utf-8")

            if query in text.lower():
                results.append(
                    f"\n[{text_path.name}]\n"
                    f"{text[:2000]}"
                )

        except Exception as error:
            results.append(
                f"[Error reading {text_path.name}: {error}]"
            )

    if not results:
        return f"No results found for: {query}"

    return "\n".join(results[:5])