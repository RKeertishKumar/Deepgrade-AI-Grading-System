import ollama
import json

# GLOBAL CONFIGURATIONS
MODEL_NAME = 'llama3.2-vision:latest'
GRADING_PROMPT = '''
You are an expert flowchart evaluator. You will be given:
  - An image of a flowchart.

Your tasks, in order:

1. Node Classification
   - List every node (by ID or label), classify it as Start, End, Process, or Decision.
   - For each classification, briefly explain your reasoning.

2. Structural & Practical Checks
   For each of the following checks:
   a) Describe how you verify it against the flowchart.
   b) State the result (True or False).

   ### Structural Logic Checks
   - LT_1: Exactly one start node and one end node
   - LT_2: All decision nodes contain clear, meaningful conditions
   - LT_3: All nodes are connected; no isolated nodes
   - LT_4: Node IDs are unique and in ascending order
   - LT_5: At least one valid path from start to end exists
   - LT_6: All node types are valid (Start, End, Process, Decision)
   - LT_7: If loops exist, each has a proper termination condition
   - LT_8: All nodes have clear, meaningful labels
   - LT_9: Each decision node has exactly two outgoing edges (e.g., Yes/No)

   ### Practical Reasoning Checks
   - PT_1: The flowchart works for a basic test case
   - PT_2: The flowchart works for a second, different test case

   ### Additional Checks
   - PT_3: It handles an edge/boundary case well
   - PT_4: It is logically efficient (solves the problem with minimal steps)

4. Final Output
   - Output the results as a JSON object with the following structure:
     {
       "checks": {
         "LT_1": true/false,
         "LT_2": true/false,
         ...
         "PT_4": true/false
       },
       "practical_questions": {
         "PT_1": {"question": "...", "reasoning": "..."},
         "PT_2": {"question": "...", "reasoning": "..."},
         ...
       }
     }

IMPORTANT: 
- Think step by step; do not skip your chain of thought.
- After your reasoning, **do not** include any extra commentary—just the JSON result.
'''

def ollama_func(question, image_path):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            'role': 'user',
            'content': GRADING_PROMPT + f"\nNow evaluate the following flowchart:\n{question}",
            'images': [image_path]
        }]
    )

    content = response['message']['content']

    # Print the raw response for debugging
    print("Raw LLM Response:", content)

    # Check if content is empty or invalid
    if not content.strip():
        raise ValueError("LLM returned an empty response. Please check the input or LLM configuration.")

    # Parse the JSON response
    # Extract JSON content starting from '{' and ending at '}'
    start_index = content.find('{')
    end_index = content.rfind('}')
    if start_index == -1 or end_index == -1 or start_index > end_index:
        raise ValueError("Failed to locate JSON content in the response.")

    json_content = content[start_index:end_index + 1]
    content = json_content
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        # Log the raw content for debugging purposes
        print("Failed to parse JSON response. Raw content:", content)
        raise ValueError("Failed to parse JSON response from LLM") from e

    return result

if __name__ == "__main__":
    question = "Evaluate the flowchart in the image."
    image_path = "1.jpg"

    try:
        response = ollama_func(question, image_path)
        print("Parsed Response:", response)
    except Exception as e:
        print("Error:", str(e))