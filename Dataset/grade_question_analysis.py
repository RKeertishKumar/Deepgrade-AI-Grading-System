import ollama
import pandas as pd
import re

MODEL = 'granite3.2-vision:latest'

grading_prompt = '''
You are an expert flowchart evaluator and classifier.

    You will be given:
    - A flowchart-related question.

    Your task is to:
    1. Classify the question into the following categories:
        - **Question Intent:** Descriptive, Diagnostic, Predictive, Prescriptive
        - **Difficulty Level:** L1 (Beginner), L2 (Intermediate), L3 (Advanced), L4 (Expert), L5 (Mastery)
        - **Evaluation Type:** Conceptual Understanding, Application, Analysis, Creativity

    2. Evaluate the flowchart in terms of structure and logic as detailed below.
    3. Extract reasoning for the classification of the question.

    ### Output Format:
    Return the following:
    - `question_intent` (Descriptive, Diagnostic, Predictive, Prescriptive)
    - `question_difficulty_level` (L1, L2, L3, L4, L5)
    - `question_evaluation_type` (Conceptual Understanding, Application, Analysis, Creativity)
    - **Evaluation Report** based on the flowchart checks (as per the original grading system).

Now, classify and evaluate the following flowchart question:
'''

def ollama_func(question, image_path):
    response = ollama.chat(
        model=MODEL,
        messages=[{
            'role': 'tool',
            'content': grading_prompt + "and here is the question: " + question,
            'images': [image_path]
        }]
    )
    
    # Parse the response to extract the classifications and grading
    matches = re.findall(r'question_intent: (.*?),\s*question_difficulty_level: (.*?),\s*question_evaluation_type: (.*?),\s*total_score: (\d+)', response['message']['content'])

    if matches:
        question_intent, difficulty_level, evaluation_type
    else:
        # Fallback if the response does not match expected format
        question_intent, difficulty_level, evaluation_type = "Unknown", "L1", "Conceptual Understanding"
    
    return question_intent, difficulty_level, evaluation_type

# Load CSV
df = pd.read_csv('grade.csv').head(1)

# Apply the function and create the new columns
df[['question_intent', 'question_difficulty_level', 'question_evaluation_type']] = df.apply(
    lambda row: pd.Series(ollama_func(row['question'], row['image'])),
    axis=1
)

# Add model name used for classification
df['question_classification_model'] = MODEL

df = df[['id','question','question_intent', 'question_difficulty_level','question_evaluation_type']]

# Save the updated DataFrame
df.to_csv('grade_question_analysis.csv', index=False)
