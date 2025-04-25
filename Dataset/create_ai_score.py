import ollama
import pandas as pd
import re
import json

# GLOBAL CONFIGURATIONS
MODEL_NAME = 'llama3.2-vision'
GRADING_PROMPT = '''You are an AI vision reasoning model. You will receive an image of a flowchart and the scope of the question it is meant to answer. Your task is to analyze the flowchart and, using the following rules, determine whether each rule is satisfied (True) or violated (False). Return your results as a JSON object, where each key is the rule_id and the value is True (rule satisfied) or False (rule violated).

        Rules:

        1. All variables used in the flowchart/diagram must be properly initialized before use.
        2. The algorithm should match the expected scope and complexity of the question.
        3. The submitted image or diagram must be clear and legible.
        4. If the diagram is too complex, contains multiple diagrams, or is ambiguous, flag false for human review.
        5. The flowchart must include an end node (terminator).
        6. All decision nodes must be clearly labeled with 'Yes/No' or appropriate conditions.
        7. Loops in the flowchart must be represented with correct loop arrows.
        8. The correct type of box/shape must be used for each node (e.g., rectangles for processes, diamonds for decisions).
        9. Every node must be properly enclosed within its designated box/shape.

        Instructions:

        - Carefully analyze the provided flowchart image and the question scope.
        - For each rule, reason whether the flowchart satisfies the rule (True) or violates it (False).
        - Return your answer as a JSON object in the following format:

        ```json
        {
        "rule_1": true,
        "rule_2": false,
        "rule_3": true,
        "rule_4": true,
        "rule_5": true,
        "rule_6": false,
        "rule_7": true,
        "rule_8": true,
        "rule_9": true
        }
        ```

        Input:

        - `flowchart_image`: [Attach or link to the image]
        - `question_scope`: [Insert the scope of the question]

        Output:

        - A JSON object with each `rule_id` as the key and a boolean value indicating if the rule is satisfied.

        ---

        **Example Input:**

        - flowchart_image: [image.png]
        - question_scope: "Design a flowchart to calculate the factorial of a number."

        **Example Output:**

        ```json
        {
        "rule_1": true,
        "rule_2": true,
        "rule_3": true,
        "rule_4": true,
        "rule_5": true,
        "rule_6": true,
        "rule_7": true,
        "rule_8": true,
        "rule_9": true
        }
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

    # Parse the JSON response using ```json and ``` delimiters
    response_text = content
    match = re.search(r'\s*(\{.*?\})\s*', response_text, re.DOTALL) 
    if match: 
        json_str = match.group(1) 
        parsed_json = json.loads(json_str) 
        print(parsed_json) 
    else: 
        print("No JSON block found.")
    

    return parsed_json

# Load CSV and select range
df = pd.read_csv('grade.csv').head(2)


expanded_results = df.apply(lambda row: ollama_func(row['question'], row['image_path']), axis=1)

result_df = pd.DataFrame(list(expanded_results))

df = pd.concat([df, result_df], axis=1)

df['model_name'] = MODEL_NAME

# Save to a new CSV file
df.to_csv("ai_grade.csv", mode='a', header=False, index=False)

