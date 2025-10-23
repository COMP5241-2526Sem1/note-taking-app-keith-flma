import os
import sys

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app from src/main.py
from src.main import app
