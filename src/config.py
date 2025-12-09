import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found")
        return True
