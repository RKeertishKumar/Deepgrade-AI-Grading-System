import ollama
import pandas as pd
import re

# GLOBAL CONFIGURATIONS
MODEL_NAME = 'gemma3:4b'
START_INDEX = 0  # Update this if needed
END_INDEX = None  # None will go till the end of the DataFrame

# UPDATED PROMPT TO CLASSIFY NODE TYPES
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

3. Scoring
   - Assign 1 point for each True, 0 for each False (13 checks total).
   - Normalize the sum to a score out of 10.
   - Show your calculation.

4. Final Output
   - First, show a concise “Reasoning” section (your step-by-step).
   - Then, output **ONLY** the following lines in plain text:
     LT_1: True/False
     LT_2: True/False
     …
     PT_4: True/False
     TOTAL_SCORE: x/10

IMPORTANT: 
- Think step by step; do not skip your chain of thought.
- Show how you arrived at each True/False.
- After your reasoning, **do not** include any extra commentary—just the result block.
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

    # Extract rule outcomes
    checks = re.findall(r'(LT_\d|PT_\d):\s*(True|False)', content)
    result = {k: v == 'True' for k, v in checks}

    # Extract normalized score
    match = re.search(r'TOTAL_SCORE:\s*(\d+(?:\.\d+)?)/10', content)
    result['ai_grade'] = float(match.group(1)) if match else None

    return result

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

result_df['ai_grade'] = expanded_results.apply(lambda x: x.get('ai_grade', None))

# Save to a new CSV file
result_df.to_csv("ai_grade.csv", index=False)
