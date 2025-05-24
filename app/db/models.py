from sqlalchemy import Column, Integer, Text, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# === Create a base class for declarative class definitions ===
Base = declarative_base()

# === Define the "papers" table as a SQLAlchemy model ===
class Paper(Base):
    __tablename__ = "papers"  # Name of the table in the database

    # === Define table columns ===
    id = Column(Integer, primary_key=True)  # Unique ID for each paper (auto-incremented)
    title = Column(Text, nullable=False)    # Title of the paper (required)
    abstract = Column(Text)                 # Abstract or summary of the paper
    source = Column(String(50))             # Source type: 'internal_upload' or 'web_search'
    created_at = Column(DateTime, server_default=func.now())  # Timestamp of creation (default: now)
