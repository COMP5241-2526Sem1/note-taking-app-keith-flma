import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Database configuration - using SQLite for simplicity
# In production, you might want to use environment variables for the database URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Enable CORS for all routes
CORS(app)

# Register blueprints
from src.routes.note import note_bp
from src.routes.user import user_bp
app.register_blueprint(note_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')

# Create database tables
with app.app_context():
    db.create_all()

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
