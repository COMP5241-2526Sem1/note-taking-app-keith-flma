from flask import Blueprint, jsonify, request
from src.models.note import Note, db
import json
import os

llm_bp = Blueprint('llm', __name__)

def check_api_availability():
    """Check if any LLM API is available"""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_TOKEN")
    return api_key is not None

@llm_bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to target language"""
    if not check_api_availability():
        return jsonify({'error': 'LLM API not configured. Translation feature disabled.'}), 503
    
    try:
        from src.llm import translate
        data = request.json
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify({'error': 'Text and target_language are required'}), 400
        
        text = data['text']
        target_language = data['target_language']
        
        translated_text = translate(text, target_language)
        
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@llm_bp.route('/extract-structured-notes', methods=['POST'])
def extract_notes():
    """Extract structured notes from text"""
    if not check_api_availability():
        return jsonify({'error': 'LLM API not configured. Extract feature disabled.'}), 503
    
    try:
        from src.llm import extract_structured_notes
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        language = data.get('language', 'English')
        
        structured_notes_json = extract_structured_notes(text, language)
        
        # Parse the JSON response from LLM
        try:
            structured_notes = json.loads(structured_notes_json)
            return jsonify(structured_notes)
        except json.JSONDecodeError:
            # If LLM didn't return valid JSON, return the raw text
            return jsonify({
                'error': 'Failed to parse structured notes',
                'raw_response': structured_notes_json
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Extract failed: {str(e)}'}), 500

@llm_bp.route('/generate-note', methods=['POST'])
def generate_note():
    """Generate a note from user input text"""
    if not check_api_availability():
        return jsonify({'error': 'LLM API not configured. Generate feature disabled.'}), 503
    
    try:
        from src.llm import extract_structured_notes
        data = request.json
        if not data or 'input_text' not in data:
            return jsonify({'error': 'input_text is required'}), 400
        
        input_text = data['input_text']
        language = data.get('language', 'English')
        
        # Extract structured notes from input
        structured_notes_json = extract_structured_notes(input_text, language)
        
        # Parse the JSON response from LLM
        try:
            structured_data = json.loads(structured_notes_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse LLM response', 'raw_response': structured_notes_json}), 500
        
        # Create a new note with the extracted data
        note = Note(
            title=structured_data.get('Title', 'Untitled'),
            content=structured_data.get('Notes', input_text),
            tags=', '.join(structured_data.get('Tags', [])) if isinstance(structured_data.get('Tags'), list) else structured_data.get('Tags', ''),
            event_date=structured_data.get('Event Date', ''),
            event_time=structured_data.get('Event Time', '')
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Generate failed: {str(e)}'}), 500
