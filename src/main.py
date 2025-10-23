import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Database configuration - using in-memory SQLite or environment variable
# For serverless, we'll use /tmp directory which is writable in Vercel
database_path = os.path.join('/tmp', 'notes.db') if os.environ.get('VERCEL') else 'sqlite:///notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{database_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app)

# Initialize database only after app is configured
from src.models.user import db
db.init_app(app)

# Register blueprints
try:
    from src.routes.note import note_bp
    from src.routes.user import user_bp
    app.register_blueprint(note_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
except Exception as e:
    print(f"Warning: Could not register blueprints: {e}")

# Create database tables (with error handling for serverless)
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")

# Root route
@app.route('/')
def index():
    return jsonify({
        'message': 'Note Taking App API',
        'status': 'running',
        'endpoints': {
            '/api/test': 'Test endpoint',
            '/api/notes': 'Notes CRUD operations',
            '/api/users': 'Users CRUD operations'
        }
    })

# Test route
@app.route('/api/test')
def test():
    return jsonify({'message': 'Hello from Flask!', 'status': 'working'})

# For Vercel deployment
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
