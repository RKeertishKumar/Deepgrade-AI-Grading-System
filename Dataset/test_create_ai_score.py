import sys
import os

# Add the parent directory to the Python path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the Dataset directory to the Python path to ensure imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd
from create_ai_score import ollama_func

class TestCreateAIScore(unittest.TestCase):

    @patch('create_ai_score.ollama.chat')
    def test_ollama_func(self, mock_chat):
        # Mock response from the LLM
        mock_response = {
            'message': {
                'content': json.dumps({
                    "checks": {
                        "LT_1": True,
                        "LT_2": False,
                        "LT_3": True,
                        "LT_4": True,
                        "LT_5": False,
                        "LT_6": True,
                        "LT_7": True,
                        "LT_8": False,
                        "LT_9": True,
                        "PT_1": True,
                        "PT_2": False,
                        "PT_3": True,
                        "PT_4": True
                    },
                    "practical_questions": {
                        "PT_1": {"question": "What is the basic test case?", "reasoning": "It works for the basic case."},
                        "PT_2": {"question": "What is the second test case?", "reasoning": "It fails for the second case."},
                        "PT_3": {"question": "What is the edge case?", "reasoning": "It handles the edge case well."},
                        "PT_4": {"question": "Is it efficient?", "reasoning": "It is logically efficient."}
                    },
                    "total_score": 7.5
                })
            }
        }

        mock_chat.return_value = mock_response

        # Input data
        question = "Sample flowchart question"
        image_path = "sample_image.jpg"

        # Call the function
        result = ollama_func(question, image_path)

        # Assertions
        self.assertEqual(result['LT_1'], True)
        self.assertEqual(result['LT_2'], False)
        self.assertEqual(result['LT_3'], True)
        self.assertEqual(result['p1_question'], "What is the basic test case?")
        self.assertEqual(result['p1_reasoning'], "It works for the basic case.")
        self.assertEqual(result['ai_grade'], 7.5)

if __name__ == '__main__':
    unittest.main()