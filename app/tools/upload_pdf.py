import pdfplumber
import os
import re
import wordninja
from app.db.db import SessionLocal
from app.db.models import Paper
from app.vector_store import embed_and_store

# === Utility functions ===

def clean_and_split(text):
    """
    Clean the text and split it into non-empty lines.
    """
    return [line.strip() for line in text.splitlines() if line.strip()]

def smart_split_words(text):
    """
    Attempt to split long concatenated words using wordninja,
    especially when the title has no spaces.
    """
    return wordninja.split(text) if len(text.split()) == 1 else text.split()

def truncate(text, max_words=100):
    """
    Truncate the text to a maximum number of words, used to shorten abstract.
    """
    words = smart_split_words(text)
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

# === Heuristic-based metadata extraction methods ===

def extract_by_position(lines):
    """
    Try to extract title and abstract based on their typical positions.
    Title is often in the first few lines; abstract is between 'abstract' and 'keywords/introduction'.
    """
    title_lines = []
    abstract_lines = []
    abstract_found = False

    for i, line in enumerate(lines):
        l = line.strip()
        if not abstract_found and re.match(r'abstract', l, re.IGNORECASE):
            abstract_found = True
            continue
        if abstract_found:
            if re.match(r'(keywords|introduction|1\.|background)', l, re.IGNORECASE):
                break
            abstract_lines.append(l)
        elif i <= 2:
            title_lines.append(l)

    title = " ".join(title_lines).strip()
    abstract = " ".join(abstract_lines).strip()
    return title, abstract

def extract_by_regex(text):
    """
    Try to extract title and abstract using regular expressions.
    """
    title_match = re.search(r"^(.*?)\babstract\b", text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Unknown Title"

    abstract_match = re.search(
        r"\babstract\b\s*[:\-]?\s*(.+?)(?=(\bkeywords\b|\bintroduction\b|1\.|\n\n))",
        text, re.IGNORECASE | re.DOTALL
    )
    abstract = abstract_match.group(1).strip() if abstract_match else "No abstract found."
    return title, abstract

def extract_semantic(text):
    """
    Detect 'abstract' sections in multiple languages using keywords.
    """
    variants = ['abstract', 'abstrak', 'résumé', 'resumen', 'مُلخّص', '摘要']
    for variant in variants:
        pattern = rf"{variant}\s*[:\-]?\s*(.+?)(?=(keywords|introduction|1\.|methods|\n\n))"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return "Unknown Title", match.group(1).strip()
    return "Unknown Title", "No abstract found."

def extract_metadata(text):
    """
    Determine the best method for extracting metadata from PDF text:
    - If very short: use regex.
    - If contains 'abstract': use position-based logic.
    - Else: fallback to semantic detection.
    Normalize the title and abstract after extraction.
    """
    lines = clean_and_split(text)
    full_text = "\n".join(lines)

    if len(lines) < 5:
        title, abstract = extract_by_regex(full_text)
    elif 'abstract' in full_text.lower():
        title, abstract = extract_by_position(lines)
    else:
        title, abstract = extract_semantic(full_text)

    title_clean = " ".join(smart_split_words(title))
    abstract_clean = truncate(abstract, max_words=120)
    return title_clean.strip(), abstract_clean.strip()

# === Main Tool Function ===

def upload_pdf(file_path: str) -> str:
    """
    Extract metadata from the first page of a PDF, store it in the database,
    and generate vector embeddings for semantic search.
    """

    # Check if the file exists
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    # Attempt to read the first page of the PDF
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0].extract_text()
    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}"

    if not first_page:
        return "❌ PDF has no extractable text."

    # Extract metadata (title and abstract)
    title, abstract = extract_metadata(first_page)

    # Save paper metadata to the database
    db = SessionLocal()
    new_paper = Paper(title=title, abstract=abstract, source="internal_upload")
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    # Store the paper's embedding in the vector store
    embed_and_store(
        doc_id=str(new_paper.id),
        text=f"{title} {abstract}",
        metadata={"source": "internal_upload", "id": new_paper.id, "title": title}
    )

    # Return a success message
    return f"✅ Uploaded paper {new_paper.id}: {title}\nAbstract: {abstract[:200]}..."
