import ollama
import pandas as pd
import re

# GLOBAL CONFIGURATIONS
MODEL_NAME = 'llama3.2-vision:11b-instruct-q4_K_M'
START_INDEX = 0  # Update this if needed
END_INDEX = 2  # None will go till the end of the DataFrame

# UPDATED PROMPT TO CLASSIFY NODE TYPES
GRADING_PROMPT = ''' 
You are an expert flowchart evaluator. 
You will be given: 
- An image of a flowchart.  
Your task is to:
1. Classify all nodes as one of the following types: Start, End, Process, Decision.  
2. Run a series of structural and practical checks listed below.  
3. Output a True or False for each check.  
4. Normalize the total score out of 10.  
5. Return your results in a structured plain text format.  
---
### Structural Logic Checks (True/False)
- LT_1: Exactly one start node and one end node
- LT_2: All decision nodes contain clear, meaningful conditions
- LT_3: All nodes are connected; no isolated nodes
- LT_4: Node IDs are unique and in ascending order
- LT_5: At least one valid path from start to end exists
- LT_6: All node types are valid (Start, End, Process, Decision)
- LT_7: If loops exist, each has a proper termination condition
- LT_8: All nodes have clear, meaningful labels
- LT_9: Each decision node has exactly two outgoing edges (e.g., Yes/No)

### Practical Reasoning Checks (True/False)
- PT_1: The flowchart works for a basic test case
- PT_2: The flowchart works for a second, different test case

### Additional Checks (True/False)
- PT_3: It handles an edge/boundary case well
- PT_4: It is logically efficient (solves the problem with minimal necessary steps)

### Final Output Format (Plain Text) Below is just an example. Properly state True or False based on flowchart.
LT_1: True
LT_2: False
LT_3: True
LT_4: True
LT_5: True
LT_6: True
LT_7: True
LT_8: True
LT_9: True
PT_1: True
PT_2: True
PT_3: True
PT_4: True
TOTAL_SCORE: 8.5/10
'''

def ollama_func(question, image_path):
    response = ollama.chat(
        model=MODEL_NAME,
        options={
            "num_gpu":0
        },
        messages=[{
            'role': 'tool',
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
df = pd.read_csv('grade.csv')

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

# Save to a new CSV file
result_df.to_csv("ai_grade.csv")
