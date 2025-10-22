import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Root route
@app.route('/')
def index():
    return jsonify({
        'message': 'Note Taking App API',
        'status': 'running',
        'endpoints': {
            '/api/test': 'Test endpoint'
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
