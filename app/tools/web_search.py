import requests
import xml.etree.ElementTree as ET
from app.db.db import SessionLocal
from app.db.models import Paper
from app.vector_store import embed_and_store
from datetime import datetime

def search_arxiv(query: str) -> str:
    """
    Search for the latest research papers on arXiv using the specified query.
    Extracts paper metadata from arXiv's API and stores them in the local database
    and vector store for semantic retrieval.
    """

    # === Construct the arXiv API URL based on the user's query ===
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{query}&start=0&max_results=3&"
        f"sortBy=submittedDate&sortOrder=descending"
    )

    # === Send the HTTP GET request to arXiv ===
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch from arXiv."

    # === Parse the XML response from arXiv ===
    root = ET.fromstring(response.content)
    ns = {"arxiv": "http://www.w3.org/2005/Atom"}  # Define namespace

    db = SessionLocal()  # Create a new DB session
    summaries = []       # Collect formatted paper summaries to return

    # === Iterate through each entry (paper) found ===
    for entry in root.findall("arxiv:entry", ns):
        # Extract title and abstract from the entry
        title = entry.find("arxiv:title", ns).text.strip().replace("\n", " ")
        abstract = entry.find("arxiv:summary", ns).text.strip().replace("\n", " ")
        created = datetime.now()  # Use current time as created_at (arXiv date parsing optional)

        # === Create and store the paper record in the database ===
        new_paper = Paper(
            title=title,
            abstract=abstract,
            source="web_search",
            created_at=created
        )
        db.add(new_paper)
        db.commit()
        db.refresh(new_paper)

        # === Store the paper's embedding in the vector store for semantic search ===
        embed_and_store(
            doc_id=str(new_paper.id),
            text=f"{title} {abstract}",
            metadata={"source": "web_search", "id": new_paper.id, "title": title}
        )

        # Add summary line for this paper
        summaries.append(f"{new_paper.id}. {title}")

    # === Return a message if no papers were found ===
    if not summaries:
        return "No papers found for the given topic on arXiv."

    # === Return formatted summary list of all inserted papers ===
    return "Top papers found on arXiv:\n" + "\n".join(summaries)
