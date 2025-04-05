import json
from app import app

def test_case_1():
    tester = app.test_client()
    response = tester.post('/classify',
                           data=json.dumps({
                               "input": {
                                   "prompt": "A flowchart is supposed to compute the factorial of N, but there is a mistake. Identify the mistake in the flowchart and explain how to correct it",
                                   "options": {
                                       "enable_types": ["logical_reasoning", "logical_verification"],
                                       "normalize_scores": True
                                   }
                               }
                           }),
                           content_type='application/json')
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert "scores" in response.json, "Response JSON does not contain 'scores'"
    print("Test Case 1 Response (Normalized Scores):", response.json)

def test_case_2():
    tester = app.test_client()
    response = tester.post('/classify',
                           data=json.dumps({
                               "input": {
                                   "prompt": "A flowchart is supposed to compute the factorial of N, but there is a mistake. Identify the mistake in the flowchart and explain how to correct it.",
                                   "options": {
                                       "enable_types": ["summarization", "information_extraction"],
                                       "normalize_scores": True
                                   }
                               }
                           }),
                           content_type='application/json')
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert "scores" in response.json, "Response JSON does not contain 'scores'"
    print("Test Case 2 Response (Normalized Scores):", response.json)

if __name__ == "__main__":
    try:
        test_case_1()
        test_case_2()
        print("All test cases passed successfully.")
    except AssertionError as e:
        print("Test case failed:", e)
