import os
import sys

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app from src/main.py
from src.main import app

# Vercel looks for 'app' or 'application' as the WSGI callable
# This is already defined in src/main.py, so we just need to import it
