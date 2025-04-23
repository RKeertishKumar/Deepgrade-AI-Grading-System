import ollama
import hashlib
import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

# Load environment variables from a .env file
load_dotenv()

class Config:
    EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "llama3.2-vision")
    CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", "granite3.2-vision")
    SEED = int(os.getenv("MODEL_SEED", 42))
    ALLOWED_EXTENSIONS = json.loads(os.getenv("ALLOWED_EXTENSIONS", '["jpg", "jpeg", "png"]'))
    MAX_SCORE = int(os.getenv("MAX_SCORE", 100))
    MIN_SCORE = int(os.getenv("MIN_SCORE", 0))

def validate_image_path(image_path: str) -> bool:
    path = Path(image_path)
    return path.exists() and path.suffix[1:].lower() in Config.ALLOWED_EXTENSIONS

def extract_json_from_response(raw_response: str) -> dict:
    start_idx = raw_response.find('{')
    end_idx = raw_response.rfind('}')
    if start_idx == -1 or end_idx == -1:
        return None
    json_str = raw_response[start_idx:end_idx+1]
    json_str = (
        json_str.strip()
        .replace('\\\n', '')
        .replace('```
        .replace('...', '')
        .replace("'", '"')
    )
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    try:
        return json.loads(json_str)
    except Exception:
        return None

def extract_flowchart_json(image_path, temperature=0.0, seed=42):
    extraction_prompt = """Convert this flowchart image to JSON with:
- "nodes": [{"id": int, "type": str, "text": str}]
- "edges": [{"from": int, "to": int, "label": str}]
Return only JSON."""
    response = ollama.chat(
        model=Config.EXTRACTION_MODEL,
        messages=[{
            'role': 'user',
            'content': extraction_prompt,
            'images': [image_path]
        }],
        options={'temperature': temperature, 'seed': seed}
    )
    return extract_json_from_response(response['message']['content'])

def classify_node_types_with_llm(nodes, temperature=0.0, seed=42):
    prompt = f"""
You are a flowchart expert. Classify each node in the following list into one of these types:
["start", "end", "input", "output", "if", "decision", "print", "process", "stack", "loop"].
If unsure, choose the closest type.
Return only valid JSON in the following format:
[
  {{"id": <node id>, "original_type": "<raw type>", "text": "<node text>", "classified_type": "<classified type>"}},
  ...
]
Nodes:
{json.dumps(nodes, indent=2)}
"""
    response = ollama.chat(
        model=Config.CLASSIFICATION_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': temperature, 'seed': seed}
    )
    start_idx = response['message']['content'].find('[')
    end_idx = response['message']['content'].rfind(']')
    if start_idx == -1 or end_idx == -1:
        return []
    json_str = response['message']['content'][start_idx:end_idx+1]
    try:
        return json.loads(json_str)
    except Exception:
        return []

def update_node_types(flowchart_json, classified_nodes):
    node_map = {item["id"]: item["classified_type"].lower() for item in classified_nodes}
    for node in flowchart_json.get("nodes", []):
        node_id = node.get("id")
        if node_id in node_map:
            node["type"] = node_map[node_id]
    return flowchart_json

def dummy_graph_score(flowchart_json):
    # For demo: grade is just the count of nodes times 10, capped at 100
    return min(len(flowchart_json.get("nodes", [])) * 10, 100)

def grade_flowchart(image_path, temperature, seed):
    flowchart_json = extract_flowchart_json(image_path, temperature=temperature, seed=seed)
    if not flowchart_json or "nodes" not in flowchart_json:
        return None
    nodes = flowchart_json["nodes"]
    classified_nodes = classify_node_types_with_llm(nodes, temperature=temperature, seed=seed)
    flowchart_json = update_node_types(flowchart_json, classified_nodes)
    score = dummy_graph_score(flowchart_json)
    return score

def temperature_tuning(image_path, runs_per_temp=3):
    temperatures = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    results = {}

    print("Temperature tuning for consistent grading:\n")
    for temp in temperatures:
        scores = []
        for i in range(runs_per_temp):
            score = grade_flowchart(image_path, temperature=temp, seed=Config.SEED + i)
            scores.append(score)
        score_counts = Counter(scores)
        most_common_score, freq = score_counts.most_common(1)
        consistent = freq == runs_per_temp
        results[temp] = {
            "scores": scores,
            "consistent": consistent,
            "most_common_score": most_common_score
        }
        print(f"Temp={temp:.1f}: Scores={scores} | Consistent: {consistent}")
    print("\nSummary Table:")
    print("Temperature | Scores           | Consistent")
    print("-------------------------------------------")
    for temp, info in results.items():
        print(f"{temp:<11} | {info['scores']} | {info['consistent']}")
    print("\nRecommendation: Use the lowest temperature that gives consistent scores for production grading.")

if __name__ == "__main__":
    image_path = "2.jpg"  # Change to your image file
    if not validate_image_path(image_path):
        print(f"ERROR: Image file '{image_path}' not found or invalid extension.")
    else:
        temperature_tuning(image_path, runs_per_temp=3)
