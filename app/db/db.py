from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base  # Import the Base metadata from your models

# === Define the connection string for your MySQL database ===
# Format: 'mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>'
DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/llm_agent'

# === Create the SQLAlchemy engine to manage the database connection ===
engine = create_engine(DATABASE_URL)

# === Create a configured "SessionLocal" class for creating session instances ===
SessionLocal = sessionmaker(bind=engine)

# === Initialize the database by creating all tables defined in models.Base ===
def init_db():
    Base.metadata.create_all(bind=engine)
