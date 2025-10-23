import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    
    # Database configuration - using /tmp for Vercel serverless
    # Note: SQLite in /tmp will be ephemeral on Vercel (resets on each cold start)
    # For production, consider using a persistent database like PostgreSQL
    if os.environ.get('VERCEL'):
        database_path = os.path.join('/tmp', 'notes.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from src.routes.note import note_bp
    from src.routes.user import user_bp
    app.register_blueprint(note_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    
    # Create database tables within app context
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
    
    return app

# Create app instance
app = create_app()

# For Vercel deployment
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
