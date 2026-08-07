import os
import sys

# Ensure backend directory is in sys.path for Vercel Serverless Function execution
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import app
