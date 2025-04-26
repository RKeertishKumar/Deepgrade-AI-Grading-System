import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OllamaService {
  private apiUrl = 'http://localhost:11434/api/chat';

  constructor(private http: HttpClient) {}

  analyzeImage(base64Image: string, userQuestion: string = ''): Observable<string> {
    const prompt = userQuestion.trim() !== '' ? 
      userQuestion : 
      `You are an AI vision reasoning model. You will receive an image of a flowchart and the scope of the question it is meant to answer. Your task is to analyze the flowchart and, using the following rules, determine whether each rule is satisfied (True) or violated (False). Return your results as a JSON object, where each key is the rule_id and the value is True (rule satisfied) or False (rule violated).

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

        Input:

        - flowchart_image: [Attach or link to the image]
        - question_scope: [Insert the scope of the question]

        Output:

        - A JSON object with each rule_id as the key and a boolean value indicating if the rule is satisfied.

        ---

        **Example Input:**

        - flowchart_image: [image.png]
        - question_scope: "Design a flowchart to calculate the factorial of a number."

        **Example Output:**

        json
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
        }`;

    const requestBody = {
      model: 'gemma3:4b',
      messages: [
        {
          role: 'user',
          content: prompt,
          images: [base64Image]
        }
      ]
    };

    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.post(this.apiUrl, requestBody, {
      headers,
      responseType: 'text'
    });
  }
}
