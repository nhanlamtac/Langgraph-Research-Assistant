from app.vector_store import query_embeddings
from app.db.db import SessionLocal
from app.db.models import Paper

def internal_search(query: str) -> str:
    """
    Perform a semantic search against the vector store for the given query,
    retrieve metadata (including paper ID), and return a summary of matched papers.
    """
    print(f"🛠️ internal_search called with: {query}")

    # === Perform semantic vector search and return associated metadata ===
    results = query_embeddings(query)

    # === Return message if no results were found ===
    if not results:
        return f"No papers found for: {query}. ✅ Task complete."

    # === Query paper metadata from the database using returned paper IDs ===
    db = SessionLocal()
    summaries = []
    for meta in results:
        paper_id = meta.get("id")  # Extract ID from metadata
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            summaries.append(f"{paper.id}. {paper.title}")  # Format summary line

    # === Compose a readable result string for the agent ===
    response = "Top matching papers:\n" + "\n".join(f"- {s}" for s in summaries)
    response += "\n✅ Done. Use these IDs to compare papers."
    return response
