"""
Flask web server for accepting form submissions from your website
Allows your site to POST form data to this local database
"""

from flask import Flask, request, jsonify
from database import db
import os

app = Flask(__name__)

# Enable CORS for local development
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print("Note: flask-cors not installed. Cross-origin requests may be restricted.")

@app.route('/api/submit-form', methods=['POST'])
def submit_form():
    """Submit form data to database"""
    try:
        data = request.get_json()
        form_name = data.get('form_name', 'generic_form')
        form_data = data.get('data', {})
        
        submission_id = db.submit_form(form_name, form_data)
        
        return jsonify({
            'status': 'success',
            'submission_id': submission_id,
            'message': f'Form "{form_name}" submitted successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/pending-reviews', methods=['GET'])
def get_pending_reviews():
    """Get all submissions pending AI review"""
    try:
        pending = db.get_pending_reviews()
        
        return jsonify({
            'status': 'success',
            'count': len(pending),
            'submissions': pending
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get recent form submissions"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        submissions = db.get_all_submissions(limit=limit)
        
        return jsonify({
            'status': 'success',
            'count': len(submissions),
            'submissions': submissions
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/mark-reviewed/<int:submission_id>', methods=['POST'])
def mark_reviewed(submission_id):
    """Mark a submission as reviewed"""
    try:
        data = request.get_json() or {}
        ai_response = data.get('ai_response', None)
        
        success = db.mark_reviewed(submission_id, ai_response)
        
        return jsonify({
            'status': 'success',
            'message': f'Submission {submission_id} marked as reviewed'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/data', methods=['POST'])
def add_data():
    """Add key-value data entry"""
    try:
        data = request.get_json()
        category = data.get('category')
        key = data.get('key')
        value = data.get('value')
        
        if not all([category, key, value is not None]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: category, key, value'
            }), 400
        
        entry_id = db.add_data(category, key, value)
        
        return jsonify({
            'status': 'success',
            'entry_id': entry_id,
            'message': 'Data entry added'
        }), 201
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/data/<category>/<key>', methods=['GET'])
def get_data(category, key):
    """Get latest value for a key in a category"""
    try:
        value = db.get_latest_data(category, key)
        
        if value is None:
            return jsonify({
                'status': 'not_found',
                'message': f'No data found for {category}/{key}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'category': category,
            'key': key,
            'value': value
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/data/<category>', methods=['GET'])
def get_category_data(category):
    """Get all data in a category"""
    try:
        entries = db.get_data_by_category(category)
        
        return jsonify({
            'status': 'success',
            'category': category,
            'count': len(entries),
            'entries': entries
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'database': 'connected' if os.path.exists(db.db_path) else 'not found'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'JARVIS Form Database API',
        'endpoints': {
            'POST /api/submit-form': 'Submit form data',
            'GET /api/pending-reviews': 'Get submissions pending AI review',
            'GET /api/submissions': 'Get recent submissions (limit parameter)',
            'POST /api/mark-reviewed/<id>': 'Mark submission as reviewed',
            'POST /api/data': 'Add key-value data entry',
            'GET /api/data/<category>': 'Get all data in category',
            'GET /api/data/<category>/<key>': 'Get specific data value',
            'GET /health': 'Check API health'
        }
    }), 200


if __name__ == '__main__':
    print("Starting JARVIS Form Database API...")
    print("API will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  POST http://localhost:5000/api/submit-form")
    print("  GET  http://localhost:5000/api/pending-reviews")
    print("  GET  http://localhost:5000/health")
    print("\nCtrl+C to stop\n")
    
    app.run(host="127.0.0.1", port=5000, debug=False)
