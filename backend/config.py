import os

class Config:
    """Centralized application configuration."""
    # Security
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-123")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///rag.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application Logic
    MAX_QUESTIONS_PER_DAY = int(os.getenv("MAX_QUESTIONS_PER_DAY", 20))

    # Path Management
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
    INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")