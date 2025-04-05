import unittest
from app import app

class PromptClassifierTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_classification(self):
        response = self.app.post('/classify', json={
            "input": {
                "prompt": "A flowchart is supposed to compute the factorial of N, but there is a mistake. Identify the mistake in the flowchart and explain how to correct it.",
                "options": {
                    "enable_types": [
                        "logical_reasoning",
                        "summarization",
                        "logical_verification",
                        "information_extraction",
                        "localization_recognition"
                    ]
                }
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('output', data)
        self.assertIn('classification', data['output'])
        self.assertEqual(len(data['output']['classification']), 5)

    def test_empty_prompt(self):
        response = self.app.post('/classify', json={
            "input": {
                "prompt": "",
                "options": {
                    "enable_types": [
                        "logical_reasoning",
                        "summarization"
                    ]
                }
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('output', data)
        self.assertIn('classification', data['output'])
        self.assertEqual(len(data['output']['classification']), 2)

if __name__ == '__main__':
    unittest.main()