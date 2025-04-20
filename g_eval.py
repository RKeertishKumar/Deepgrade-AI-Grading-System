import ollama
import hashlib
import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Central configuration management class."""
    # Model for extracting JSON from image
    EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "llama3.2-vision")
    # Model for classifying node types
    CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", "granite3.2-vision")
    # Parameters for both LLM calls
    TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0))
    SEED = int(os.getenv("MODEL_SEED", 42))
    ALLOWED_EXTENSIONS = json.loads(os.getenv("ALLOWED_EXTENSIONS", '["jpg", "jpeg", "png"]'))
    MAX_SCORE = int(os.getenv("MAX_SCORE", 100))
    MIN_SCORE = int(os.getenv("MIN_SCORE", 0))

def validate_image_path(image_path: str) -> bool:
    """Ensure the image file exists and has an allowed extension."""
    path = Path(image_path)
    return path.exists() and path.suffix[1:].lower() in Config.ALLOWED_EXTENSIONS

def fix_quotes_in_values(json_str: str) -> str:
    """
    Heuristically fix unescaped double quotes within JSON string values.
    """
    def replacer(match):
        prefix = match.group(1)
        content = match.group(2)
        suffix = match.group(3)
        fixed_content = re.sub(r'(?<!\\)"', r'\\"', content)
        return f"{prefix}{fixed_content}{suffix}"
    pattern = re.compile(r'(:\s*")([^"]*?)(")')
    fixed_str = pattern.sub(replacer, json_str)
    return fixed_str

def extract_json_from_response(raw_response: str) -> dict:
    """
    Extract and clean the JSON portion from an LLM response.
    This function grabs text from the first '{' to the last '}' and
    attempts to load it. If that fails, it applies heuristic fixes.
    """
    # Grab content between the first '{' and the last '}'
    start_idx = raw_response.find('{')
    end_idx = raw_response.rfind('}')
    if start_idx == -1 or end_idx == -1:
        return None
    json_str = raw_response[start_idx:end_idx+1]
    json_str = (
        json_str.strip()
        .replace('\\\n', '')
        .replace('```', '')
        .replace('...', '')
        .replace("'", '"')
    )
    # Remove trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print("Problematic JSON:", json_str)
        fixed_json_str = fix_quotes_in_values(json_str)
        try:
            return json.loads(fixed_json_str)
        except json.JSONDecodeError as e2:
            print(f"Fixed JSON still fails: {e2}")
            print("Fixed JSON:", fixed_json_str)
            return None

def normalize_flowchart_json(flowchart_json: dict) -> dict:
    """
    Normalize the flowchart JSON structure.
    For example, if the "path" key is not a list, wrap it in a list.
    """
    if "path" in flowchart_json and not isinstance(flowchart_json["path"], list):
        flowchart_json["path"] = [flowchart_json["path"]]
    return flowchart_json

# -------------------------
# LLM‐Based Node Type Classification
# -------------------------
# Allowed node types for our application
VALID_NODE_TYPES = {"start", "end", "input", "output", "if", "decision", "print", "process", "stack", "loop"}

def classify_node_types_with_llm(nodes: list) -> list:
    """
    Use the LLM to classify node types.

    The prompt sends the list of nodes (with id, original type, and text)
    and asks the LLM to assign one of the allowed types. The response should be
    a JSON array with entries like:
    {"id": <node id>, "original_type": "<raw type>", "text": "<node text>", "classified_type": "<classified type>"}
    """
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
        options={'temperature': 0, 'seed': Config.SEED}
    )
    # Extract the JSON array from the response. We assume that the response
    # contains a JSON array starting at the first '['.
    start_idx = response['message']['content'].find('[')
    end_idx = response['message']['content'].rfind(']')
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Failed to find JSON array in classification response.")
    json_str = response['message']['content'][start_idx:end_idx+1]
    try:
        classified_nodes = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Error decoding classified nodes:", e)
        classified_nodes = []
    return classified_nodes

def update_node_types(flowchart_json: dict, classified_nodes: list) -> dict:
    """
    Update the node types in the flowchart JSON using the classified results.
    """
    node_map = {item["id"]: item["classified_type"].lower() for item in classified_nodes}
    for node in flowchart_json.get("nodes", []):
        node_id = node.get("id")
        if node_id in node_map:
            node["type"] = node_map[node_id]
    return flowchart_json

# -------------------------
# Graph-Based Logic Tests
# -------------------------
def test_start_end(flowchart_json: dict):
    """LT_1: Check that there is exactly one start and one end node. Weight = 30"""
    nodes = flowchart_json.get("nodes", [])
    start_count = sum(1 for n in nodes if n.get("type") == "start")
    end_count = sum(1 for n in nodes if n.get("type") == "end")
    passed = (start_count == 1 and end_count == 1)
    return passed, 30, ("Start/End nodes are correct." if passed else "There must be exactly one start and one end node.")

def test_decision_condition(flowchart_json: dict):
    """LT_2: Check that decision (if/decision) nodes have a clear condition. Weight = 40"""
    nodes = flowchart_json.get("nodes", [])
    decision_nodes = [n for n in nodes if n.get("type") in {"if", "decision"}]
    passed = True
    for node in decision_nodes:
        cond = node.get("text", "").strip()
        if not cond or not any(op in cond for op in ["==", ">=", "<=", ">", "<"]):
            passed = False
            break
    return passed, 40, ("Decision nodes include proper conditions." if passed else "One or more decision nodes are missing valid conditions.")

def test_connectivity(flowchart_json: dict):
    """LT_3: Check that all nodes are connected (no orphan nodes). Weight = 30"""
    nodes = flowchart_json.get("nodes", [])
    edges = flowchart_json.get("edges", [])
    connected_ids = set()
    for edge in edges:
        connected_ids.add(edge.get("from"))
        connected_ids.add(edge.get("to"))
    all_ids = {n.get("id") for n in nodes}
    passed = all_ids and all_ids.issubset(connected_ids)
    return passed, 30, ("All nodes are connected." if passed else "There are orphan nodes (nodes that are not connected).")

def test_sequence_order(flowchart_json: dict):
    """LT_4: Check that node IDs are unique and in ascending order. Weight = 20"""
    nodes = flowchart_json.get("nodes", [])
    ids = [n.get("id") for n in nodes]
    unique_ids = set(ids)
    if len(unique_ids) != len(ids):
        return False, 20, "Node IDs are not unique."
    if ids != sorted(ids):
        return False, 20, "Node IDs are not in ascending order."
    return True, 20, "Node IDs are unique and in ascending order."

def test_path_existence(flowchart_json: dict):
    """LT_5: Check that there is at least one valid path from the start node to the end node. Weight = 20"""
    nodes = flowchart_json.get("nodes", [])
    edges = flowchart_json.get("edges", [])
    start_ids = [n.get("id") for n in nodes if n.get("type") == "start"]
    end_ids = [n.get("id") for n in nodes if n.get("type") == "end"]
    if not start_ids or not end_ids:
        return False, 20, "Start or end node is missing."
    adj = {}
    for edge in edges:
        frm = edge.get("from")
        to = edge.get("to")
        if frm is not None and to is not None:
            adj.setdefault(frm, []).append(to)
    visited = set()
    queue = start_ids.copy()
    found = False
    while queue:
        current = queue.pop(0)
        if current in end_ids:
            found = True
            break
        if current in visited:
            continue
        visited.add(current)
        queue.extend(adj.get(current, []))
    return found, 20, ("A valid path exists from start to end." if found else "No valid path found from start to end.")

def test_node_type_consistency(flowchart_json: dict):
    """LT_6: Check that every node's type is within the allowed set. Weight = 20"""
    nodes = flowchart_json.get("nodes", [])
    invalid_nodes = [n for n in nodes if n.get("type") not in VALID_NODE_TYPES]
    passed = (len(invalid_nodes) == 0)
    return passed, 20, ("All node types are valid." if passed else f"Invalid node types found: {[n.get('type') for n in invalid_nodes]}")

LOGIC_TESTS = {
    "LT_1": test_start_end,
    "LT_2": test_decision_condition,
    "LT_3": test_connectivity,
    "LT_4": test_sequence_order,
    "LT_5": test_path_existence,
    "LT_6": test_node_type_consistency
}

def run_logic_tests(flowchart_json: dict, selected_logic_ids: list) -> (int, list):
    """
    Run the selected logic tests on the flowchart JSON.
    Return a normalized score (based on Config.MAX_SCORE) and test details.
    """
    total_score = 0
    total_weight = 0
    details = []
    for lid in selected_logic_ids:
        test_func = LOGIC_TESTS.get(lid)
        if test_func:
            passed, weight, message = test_func(flowchart_json)
            details.append({
                "logic_id": lid,
                "passed": passed,
                "weight": weight,
                "message": message
            })
            total_weight += weight
            if passed:
                total_score += weight
    normalized_score = (total_score / total_weight) * Config.MAX_SCORE if total_weight > 0 else 0
    return normalized_score, details

# -------------------------
# Extraction Retry Logic
# -------------------------
def is_extraction_valid(flowchart_json: dict) -> bool:
    """
    Verify that the extracted JSON includes required keys ("nodes" and "edges")
    and that node types appear acceptable.
    """
    if not flowchart_json or "nodes" not in flowchart_json or "edges" not in flowchart_json:
        return False
    valid, _, _ = test_node_type_consistency(flowchart_json)
    return valid

def extract_flowchart_json_with_retry(image_path: str, max_attempts: int = 3) -> dict:
    """
    Attempt to extract and normalize the flowchart JSON.
    If the extraction is not valid (e.g. missing keys or invalid node types),
    retry with modified parameters (incrementing temperature and seed) up to max_attempts.
    """
    current_temp = Config.TEMPERATURE
    current_seed = Config.SEED
    attempt = 0
    extraction_prompt = """Convert this flowchart image to JSON with:
- "nodes": [{"id": int, "type": str, "text": str}]
- "edges": [{"from": int, "to": int, "label": str}]
Return only JSON."""
    extracted = None
    while attempt < max_attempts:
        response = ollama.chat(
            model=Config.EXTRACTION_MODEL,
            messages=[{
                'role': 'user',
                'content': extraction_prompt,
                'images': [image_path]
            }],
            options={'temperature': current_temp, 'seed': current_seed}
        )
        extracted = extract_json_from_response(response['message']['content'])
        if extracted:
            extracted = normalize_flowchart_json(extracted)
        if extracted and is_extraction_valid(extracted):
            print(f"Extraction succeeded on attempt {attempt+1} with temperature {current_temp}")
            return extracted
        else:
            print(f"Extraction attempt {attempt+1} failed validation. Retrying with increased temperature.")
            current_temp = min(current_temp + 0.2, 1.0)
            current_seed += 1
            attempt += 1
    return extracted

# -------------------------
# LLM-Assisted Logic Selection (Optional)
# -------------------------
def choose_logic_ids(problem_description: str) -> list:
    """Return all available logic test IDs. (This could be refined via an LLM call.)"""
    return list(LOGIC_TESTS.keys())

# -------------------------
# High-Level Evaluation Function
# -------------------------
def graph_based_g_eval(image_path: str, problem_description: str) -> dict:
    """
    Evaluate a flowchart image by first extracting its JSON (with retry if needed),
    then classifying node types via an LLM, updating the JSON, and finally running
    graph-based logic tests on the updated JSON.
    """
    result = {
        "image_hash": "",
        "score": 0,
        "details": {"logic_results": [], "classification": []},
        "flowchart_json": {},
        "error": None,
        "config": {
            "extraction_model": Config.EXTRACTION_MODEL,
            "classification_model": Config.CLASSIFICATION_MODEL,
            "grading_logic": "Graph Analysis",
            "temperature": Config.TEMPERATURE,
            "seed": Config.SEED
        }
    }
    try:
        if not validate_image_path(image_path):
            raise ValueError(f"Invalid image file: {image_path}")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            result["image_hash"] = hashlib.sha256(image_bytes).hexdigest()
        # --- Phase 1: Extraction (with retry) ---
        flowchart_json = extract_flowchart_json_with_retry(image_path, max_attempts=3)
        if not flowchart_json:
            raise ValueError("Failed to extract valid JSON from extraction response.")
        result["flowchart_json"] = flowchart_json

        # --- Phase 2: Node Type Classification via LLM ---
        nodes_raw = flowchart_json.get("nodes", [])
        if nodes_raw:
            classified_nodes = classify_node_types_with_llm(nodes_raw)
            result["details"]["classification"] = classified_nodes
            # Update the JSON with the classified node types.
            flowchart_json = update_node_types(flowchart_json, classified_nodes)
            result["flowchart_json"] = flowchart_json

        # --- Phase 3: Graph-Based Logic Evaluation ---
        selected_logic_ids = choose_logic_ids(problem_description)
        score, logic_details = run_logic_tests(flowchart_json, selected_logic_ids)
        result["score"] = score
        result["details"]["logic_results"] = logic_details

    except Exception as e:
        result["error"] = str(e)
        return result

    return result

if __name__ == "__main__":
    # Example usage – adjust the image path and problem description as needed.
    result = graph_based_g_eval(
        image_path="2.jpg",
        problem_description="Check the logic for handling stack overflow."
    )
    print(json.dumps(result, indent=2))
