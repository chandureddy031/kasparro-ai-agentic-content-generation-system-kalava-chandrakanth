"""Configuration settings loaded from environment variables."""
import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)


class Config:
    """Application configuration."""
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")  # Configurable with fallback
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration.
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If required config is missing
        """
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment")
        return True
