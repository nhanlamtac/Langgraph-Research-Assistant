from app.db.db import SessionLocal
from app.db.models import Paper

def list_papers(_: str = "") -> str:
    """
    Fetch all papers from the database and return a formatted list of their IDs and titles.
    This function is used by the LangGraph agent to let users see what papers are available.
    The argument (_) is unused, but required for compatibility with the agent tool interface.
    """
    
    # === Create a new database session ===
    db = SessionLocal()

    # === Query all papers sorted by ID ===
    papers = db.query(Paper).order_by(Paper.id).all()

    # === Return a message if no papers are found ===
    if not papers:
        return "No papers found in the database."

    # === Format paper list into a readable string ===
    response = "📚 List of Papers:\n"
    for paper in papers:
        response += f"- {paper.id}. {paper.title}\n"

    return response
