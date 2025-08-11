import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Qdrant Configuration
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION = "properties"
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-3.5-turbo"
    
    # Data Configuration
    PROPERTY_DATA_PATH = "data/properties.csv"
    
    # Email Reporting
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")
    
    # Lead Scoring
    LEAD_SCORE_WEIGHTS = {
        'contact_shared': 30,
        'detailed_questions': 20,
        'multiple_properties_viewed': 15,
        'repeated_visits': 10,
        'quick_exit': -10
    }