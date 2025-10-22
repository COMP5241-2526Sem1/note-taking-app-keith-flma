import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.models.note import Note
from src.llm import translate, extract_structured_notes

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')
# Configure database - prefer DATABASE_URL (Supabase/Postgres), fallback to local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

# Global variables for hybrid approach
supabase_client = None
use_supabase_rest = False

if DATABASE_URL:
    try:
        # Try to use Supabase Postgres connection
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        print("✅ Using Supabase Postgres database")
        
        # Also initialize Supabase client as backup
        if SUPABASE_URL and SUPABASE_ANON_KEY:
            try:
                from supabase import create_client
                supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                print("✅ Supabase REST client initialized as backup")
            except ImportError:
                print("⚠️  Supabase client not available - install with: pip install supabase")
            except Exception as e:
                print(f"⚠️  Supabase client initialization failed: {e}")
        
    except Exception as e:
        print(f"⚠️  Database configuration error: {e}")
        # Fallback to in-memory SQLite for serverless
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tmp/app.db"
        print("⚠️  Falling back to temporary SQLite database")
else:
    # Check if we're in Vercel environment
    if os.environ.get('VERCEL'):
        # Use in-memory SQLite for Vercel (serverless)
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tmp/app.db"
        print("⚠️  Using temporary SQLite database (Vercel environment)")
    else:
        # Local development - use file-based SQLite
        ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        DB_PATH = os.path.join(ROOT_DIR, 'database', 'app.db')
        # ensure database directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
        print("⚠️  Using local SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Try to create tables, with fallback handling
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️  Database connection issue: {e}")
        if supabase_client:
            print("💡 Will use Supabase REST API for database operations")
            use_supabase_rest = True
        else:
            print("❌ No database connection available")

@app.route('/api/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'English')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        translated_text = translate(text, target_language)
        return jsonify({'translated_text': translated_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-structured-notes', methods=['POST'])
def extract_notes():
    try:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('language', 'English')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        structured_notes_json = extract_structured_notes(text, lang)
        
        # Parse the JSON response
        import json
        structured_notes = json.loads(structured_notes_json)
        return jsonify(structured_notes)
    
    except json.JSONDecodeError as e:
        return jsonify({'error': 'Failed to parse structured notes'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-note', methods=['POST'])
def generate_note():
    try:
        data = request.get_json()
        input_text = data.get('input_text', '')
        language = data.get('language', 'English')
        
        if not input_text:
            return jsonify({'error': 'Input text is required'}), 400
        
        # Generate structured notes using LLM
        structured_response = extract_structured_notes(input_text, language)
        
        # Try to parse JSON response
        import json
        try:
            structured_data = json.loads(structured_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', structured_response, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group())
            else:
                return jsonify({'error': 'Failed to parse structured response'}), 500
        
        # Create and save the note
        max_order = db.session.query(db.func.max(Note.order_index)).scalar() or 0
        note = Note(
            title=structured_data.get('Title', 'Generated Note'),
            content=structured_data.get('Notes', input_text),
            event_date=structured_data.get('Event Date', ''),
            event_time=structured_data.get('Event Time', ''),
            order_index=max_order + 1
        )
        
        db.session.add(note)
        db.session.commit()
        
        # Return the created note along with extracted tags
        response_data = note.to_dict()
        response_data['tags'] = structured_data.get('Tags', [])
        
        return jsonify(response_data), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


# For Vercel deployment
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
