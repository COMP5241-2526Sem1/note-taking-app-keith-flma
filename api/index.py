from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Note Taking App API',
        'status': 'running',
        'endpoints': {
            '/api/test': 'Test endpoint'
        }
    })

@app.route('/api/test')
def test():
    return jsonify({'message': 'Hello from Flask!', 'status': 'working'})
