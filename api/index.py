from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'Note Taking App API - Simple Test',
        'status': 'running'
    })

@app.route('/api/test')
def test():
    return jsonify({'message': 'Hello from Flask!', 'status': 'working'})
