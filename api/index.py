import os
import sys

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app

# Vercel expects the Flask app to be directly exposed
# The app variable is what Vercel will use as the WSGI application
application = app

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
