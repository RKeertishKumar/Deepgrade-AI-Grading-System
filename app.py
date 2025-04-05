from flask import Flask, request, jsonify
from classifier import classify_prompt

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify_prompt_endpoint():
    data = request.json
    prompt = data.get('input', {}).get('prompt', '')
    
    # Use the updated classify_prompt function
    classification = classify_prompt(prompt)
    
    response = {
        "output": {
            "prompt": prompt,
            "classification": classification
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=7000)