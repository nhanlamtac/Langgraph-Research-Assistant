import os
from openai import OpenAI
from dotenv import load_dotenv
import chromadb

# === Load environment variables from .env file (e.g., for API key) ===
load_dotenv()

# === Initialize the OpenAI client with your API key ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Initialize Chroma vector store and create a collection named "papers" ===
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("papers")

def get_openai_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text using OpenAI's embedding model.
    Returns a list of floats (the embedding).
    """
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding

def embed_and_store(doc_id: str, text: str, metadata: dict):
    """
    Embed the given text and store it in ChromaDB along with its metadata and document ID.
    The metadata should include fields like 'title', 'source', and paper 'id'.
    """
    embedding = get_openai_embedding(text)
    collection.add(
        documents=[text],  # Store the full document text (e.g., title + abstract)
        embeddings=[embedding],
        metadatas=[{**metadata, "id": doc_id}],  # Store metadata including paper ID
        ids=[doc_id]
    )

def query_embeddings(query: str):
    """
    Perform a semantic search in the vector store for the given query.
    Returns a list of metadata dictionaries corresponding to the top 3 matched documents.
    """
    embedding = get_openai_embedding(query)
    results = collection.query(query_embeddings=[embedding], n_results=3)

    metadatas = results.get("metadatas", [[]])
    return metadatas[0] if metadatas else []
