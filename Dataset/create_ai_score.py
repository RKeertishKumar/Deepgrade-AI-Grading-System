import ollama
import pandas as pd
import re
import json

# GLOBAL CONFIGURATIONS
MODEL_NAME = 'gemma3:4b'
START_INDEX = 0  # Update this if needed
END_INDEX = None  # None will go till the end of the DataFrame

# Updated GRADING_PROMPT with specific PT_1 to PT_4 questions
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
   - LT_7: If loops exist, each has a proper termination condition (default to True if no loops exist)
   - LT_8: All nodes have clear, meaningful labels
   - LT_9: Each decision node has exactly two outgoing edges (e.g., Yes/No)

   ### Practical Reasoning Checks
   - PT_1: Does the flowchart correctly handle sorting an array of integers in ascending order?
   - PT_2: Does the flowchart correctly handle finding the maximum value in an array of integers?
   - PT_3: Does the flowchart correctly handle reversing a string input?
   - PT_4: Does the flowchart correctly handle calculating the factorial of a given number?

3. Scoring
   - Assign 1 point for each True, 0 for each False (13 checks total).
   - Normalize the sum to a score out of 10.
   - Show your calculation.

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
       },
       "total_score": x/10
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

    # Parse the JSON response using ```json and ``` delimiters
    try:
        json_start = content.find("```json") + len("```json")
        json_end = content.rfind("```")
        json_content = content[json_start:json_end].strip()
        result = json.loads(json_content)
    except json.JSONDecodeError as e:
        # Log the raw content for debugging purposes
        print("Failed to parse JSON response. Raw content:", content)
        raise ValueError("Failed to parse JSON response from LLM") from e

    # Flatten the JSON structure for DataFrame compatibility
    checks = result.get('checks', {})
    practical_questions = result.get('practical_questions', {})

    flattened_result = {**checks}
    for i in range(1, 5):
        pt_key = f'PT_{i}'
        flattened_result[f'p{i}_question'] = practical_questions.get(pt_key, {}).get('question', None)
        flattened_result[f'p{i}_reasoning'] = practical_questions.get(pt_key, {}).get('reasoning', None)

    flattened_result['ai_grade'] = result.get('total_score', None)

    return flattened_result

# Load CSV and select range
df = pd.read_csv('grade.csv').head(1)

if END_INDEX is None:
    END_INDEX = len(df)

# Apply function and expand results into multiple columns
result_df = df.iloc[START_INDEX:END_INDEX].copy()
expanded_results = result_df.apply(lambda row: ollama_func(row['question'], row['image']), axis=1)

# Assign each check result to individual columns, with None if the check is not available
result_df['LT_1'] = expanded_results.apply(lambda x: x.get('LT_1', None))
result_df['LT_2'] = expanded_results.apply(lambda x: x.get('LT_2', None))
result_df['LT_3'] = expanded_results.apply(lambda x: x.get('LT_3', None))
result_df['LT_4'] = expanded_results.apply(lambda x: x.get('LT_4', None))
result_df['LT_5'] = expanded_results.apply(lambda x: x.get('LT_5', None))
result_df['LT_6'] = expanded_results.apply(lambda x: x.get('LT_6', None))
result_df['LT_7'] = expanded_results.apply(lambda x: x.get('LT_7', None))
result_df['LT_8'] = expanded_results.apply(lambda x: x.get('LT_8', None))
result_df['LT_9'] = expanded_results.apply(lambda x: x.get('LT_9', None))
result_df['PT_1'] = expanded_results.apply(lambda x: x.get('PT_1', None))
result_df['PT_2'] = expanded_results.apply(lambda x: x.get('PT_2', None))
result_df['PT_3'] = expanded_results.apply(lambda x: x.get('PT_3', None))
result_df['PT_4'] = expanded_results.apply(lambda x: x.get('PT_4', None))

# Add practical questions and reasoning columns
for i in range(1, 5):
    result_df[f'p{i}_question'] = expanded_results.apply(lambda x: x.get(f'p{i}_question', None))
    result_df[f'p{i}_reasoning'] = expanded_results.apply(lambda x: x.get(f'p{i}_reasoning', None))

cols = ['LT_1','LT_2','LT_3','LT_4','LT_5','LT_6','LT_7','LT_8','LT_9',
        'PT_1','PT_2','PT_3','PT_4']

# Replace None with False, then cast True→1, False→0
for c in cols:
    # 1) cast to pandas nullable Boolean
    # 2) fill missing with False (or True if that’s what you intended)
    # 3) cast to plain Python int
    result_df[c] = (
        result_df[c]
          .astype('boolean')     # nullable bool dtype → no downcast warning
          .fillna(False)         # or .fillna(True) per your logic
          .astype(int)           # now safe to cast to 0/1 ints
    )
# Raw total = sum of the 13 indicator columns
result_df['total_score_raw'] = result_df[cols].sum(axis=1)

# Normalize to 10-point scale: (raw / 13) * 10
result_df['ai_grade'] = round(result_df['total_score_raw'] * 10.0 / len(cols), 0)

result_df['model_name'] = MODEL_NAME

# Save to a new CSV file
result_df.to_csv("ai_grade.csv", index=False)
