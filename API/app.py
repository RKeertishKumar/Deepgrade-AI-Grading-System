from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME')]
responses_collection = db['graded_responses']

# Grading criteria (matches your Angular frontend)
GRADING_CRITERIA = [
    {
        'name': 'Correct Algorithm',
        'pattern': re.compile(r'(correct algorithm|proper steps|accurate logic)', re.IGNORECASE),
        'weight': 30
    },
    {
        'name': 'Flowchart Structure',
        'pattern': re.compile(r'(begin|start|end|terminator|decision|process)', re.IGNORECASE),
        'weight': 25
    },
    {
        'name': 'Variable Usage',
        'pattern': re.compile(r'(variable|declare|initialize|assign)', re.IGNORECASE),
        'weight': 20
    },
    {
        'name': 'Loop Logic',
        'pattern': re.compile(r'(while|for|loop|repeat|until)', re.IGNORECASE),
        'weight': 15
    },
    {
        'name': 'Output Mention',
        'pattern': re.compile(r'(output|print|display|result)', re.IGNORECASE),
        'weight': 10
    }
]

def calculate_score(response_text):
    score = 0
    matched_criteria = []
    
    for criteria in GRADING_CRITERIA:
        is_matched = bool(criteria['pattern'].search(response_text))
        if is_matched:
            score += criteria['weight']
            matched_criteria.append(criteria['name'])
    
    # Determine score color
    if score >= 80:
        score_color = '#4CAF50'  # Green
    elif score >= 50:
        score_color = '#FFC107'  # Yellow
    else:
        score_color = '#F44336'  # Red
    
    return {
        'score': score,
        'max_score': 100,
        'score_color': score_color,
        'matched_criteria': matched_criteria
    }

@app.route('/api/grade', methods=['POST'])
def grade_response():
    data = request.json
    response_text = data.get('response')
    
    if not response_text:
        return jsonify({'error': 'No response provided'}), 400
    
    # Calculate score
    grading_result = calculate_score(response_text)
    
    # Store in MongoDB
    response_doc = {
        'response_text': response_text,
        'score': grading_result['score'],
        'score_color': grading_result['score_color'],
        'matched_criteria': grading_result['matched_criteria'],
        'timestamp': datetime.utcnow()
    }
    
    inserted = responses_collection.insert_one(response_doc)
    
    return jsonify({
        'id': str(inserted.inserted_id),
        **grading_result,
        'formatted_response': format_response(response_text, grading_result['matched_criteria'])
    })

def format_response(response_text, matched_criteria):
    # Basic formatting similar to your frontend - USING PYTHON re.sub() instead of JS regex
    formatted = re.sub(r'\*\s*(.*?)\n', r'<li>\1</li>', response_text)
    formatted = f'<ul>{formatted}</ul>'
    
    # Highlight phrases
    highlight_phrases = ['Read:', 'If', 'Result =', 'Beg =', 'End =', 'Mid =']
    for phrase in highlight_phrases:
        formatted = formatted.replace(phrase, f'<strong>{phrase}</strong>')
    
    return formatted

if __name__ == '__main__':
    app.run(debug=True, port=5000)