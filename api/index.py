import os
import sys

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app

# Vercel serverless function entry point
# The 'app' variable is what Vercel will use
def handler(request):
    return app(request.environ, lambda *args: None)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
