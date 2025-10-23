import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.models.user import db

def create_app():
    # Set the static folder path
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    
    # Database configuration
    # Priority: DATABASE_URL env var (Supabase) > local SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Use Supabase PostgreSQL (production)
        # Fix for IPv6 issue: add options to force IPv4
        if 'postgresql://' in database_url or 'postgres://' in database_url:
            # Ensure sslmode is set for Supabase
            if '?' not in database_url:
                database_url = f"{database_url}?sslmode=require"
            elif 'sslmode' not in database_url:
                database_url = f"{database_url}&sslmode=require"
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        # Add engine options for better connection handling
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 5,
            'max_overflow': 10,
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 10,
            }
        }
    elif os.environ.get('VERCEL'):
        # Fallback to ephemeral SQLite in /tmp for Vercel (if DATABASE_URL not set)
        database_path = os.path.join('/tmp', 'notes.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    else:
        # Local development SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from src.routes.note import note_bp
    from src.routes.user import user_bp
    app.register_blueprint(note_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    
    # Register LLM blueprint (optional - works only if API keys are configured)
    try:
        from src.routes.llm import llm_bp
        app.register_blueprint(llm_bp, url_prefix='/api')
    except Exception as e:
        print(f"Warning: LLM routes not available: {e}")
    
    # Create database tables within app context (with error handling)
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        # Tables might already exist, which is fine
    
    # Root route - serve the HTML file
    @app.route('/')
    def index():
        return send_from_directory(static_folder, 'index.html')
    
    # Serve static files
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(static_folder, 'favicon.ico')
    
    # API info route
    @app.route('/api')
    def api_info():
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
    
    # Database test route
    @app.route('/api/db-test')
    def db_test():
        try:
            # Try to query the database
            from src.models.note import Note
            count = Note.query.count()
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            # Hide password in response
            if 'postgresql://' in db_uri:
                db_type = 'PostgreSQL (Supabase)'
                db_uri_safe = db_uri.split('@')[1] if '@' in db_uri else 'Connected'
            else:
                db_type = 'SQLite'
                db_uri_safe = db_uri
            
            return jsonify({
                'status': 'Database connected',
                'database_type': db_type,
                'database_location': db_uri_safe,
                'notes_count': count
            })
        except Exception as e:
            return jsonify({
                'status': 'Database error',
                'error': str(e)
            }), 500
    
    return app

# Create app instance
app = create_app()

# For Vercel deployment
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
