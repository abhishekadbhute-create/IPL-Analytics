import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DEBUG = True
    PORT = 5000
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
