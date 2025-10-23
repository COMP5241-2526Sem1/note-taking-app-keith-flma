import os
import sys

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    # Import the Flask app from src/main.py
    from src.main import app
except Exception as e:
    # Fallback: create a minimal Flask app if import fails
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Note Taking App API (Fallback)',
            'status': 'running',
            'error': str(e)
        })
    
    @app.route('/api/test')
    def test():
        return jsonify({'message': 'Hello from Flask!', 'status': 'working', 'note': 'Using fallback app'})

# Vercel looks for 'app' or 'application' as the WSGI callable
# This is already defined in src/main.py, so we just need to import it
