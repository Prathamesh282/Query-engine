from pydantic import BaseModel

class Settings(BaseModel):
    """Configuration settings for the application."""
    # Embedding model settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384 # Dimension for the chosen model
    
    #LLM settings
    LLM_MODEL: str = "ollama/llama3:8b" 

    # Document processing settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

# Create a single instance of the settings to be used throughout the app
settings = Settings()