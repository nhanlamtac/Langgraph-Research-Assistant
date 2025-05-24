from app.db.db import SessionLocal
from app.db.models import Paper
from langchain_openai import ChatOpenAI
import re

# === Initialize the LLM (GPT-3.5) with zero temperature for deterministic output ===
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def compare_papers(query: str) -> str:
    """
    Compare two papers given their IDs from a user's query like: "Compare paper 10 and 21"
    Returns a structured comparison using the LLM.
    """

    # === Extract numeric paper IDs from the input string using regex ===
    ids = list(map(int, re.findall(r"\d+", query)))
    if len(ids) < 2:
        return "❌ Please specify two paper IDs to compare, like 'Compare paper 1 and 2'."

    # === Open a database session and fetch both papers by ID ===
    db = SessionLocal()
    paper1 = db.query(Paper).filter(Paper.id == ids[0]).first()
    paper2 = db.query(Paper).filter(Paper.id == ids[1]).first()

    # === Return an error message if one or both papers are not found ===
    if not paper1 or not paper2:
        return f"❌ One or both paper IDs not found: {ids[0]}, {ids[1]}."

    # === Construct a structured comparison prompt for the LLM ===
    prompt = f"""
Compare the following two research papers:

Paper 1:
Title: {paper1.title}
Abstract: {paper1.abstract}

Paper 2:
Title: {paper2.title}
Abstract: {paper2.abstract}

Provide a structured comparison including:
- Research Goals
- Methods
- Key Contributions
- Strengths and Weaknesses
- Similarities and Differences
Limit your response to 300 words.
"""

    # === Call the LLM and return the generated comparison or an error message ===
    try:
        response = llm.invoke(prompt)
        return response.content + "\n✅ Done comparing papers."
    except Exception as e:
        return f"❌ Error during comparison: {str(e)}"
