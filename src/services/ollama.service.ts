import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OllamaService {
  private apiUrl = 'http://localhost:11434/api/chat';

  constructor(private http: HttpClient) {}

  analyzeImage(base64Image: string): Observable<string> {
    const FLOWCHART_EVALUATION_PROMPT = `
    You are an expert flowchart evaluator.

    You will be given:
    - An image of a flowchart.
    - A flag: \`use_professional_checks\`, which is either \`true\` or \`false\`.

    Your task is to:
    1. Extract the nodes, edges, and labels from the flowchart.
    2. Run a series of structural and practical checks.
    3. Score each check with the weight assigned.
    4. Provide reasoning for each score.
    5. Normalize the total score to 100.
    6. Return the results in plain text format suitable for displaying to a student or professional.

    ---

    ### Structural Logic Checks (Applicable to All)

    - **LT_1 (30 pts):** Check that the flowchart has exactly one start node and one end node.
    - **LT_2 (40 pts):** Ensure that all decision nodes contain clear, meaningful conditions.
    - **LT_3 (30 pts):** Verify that all nodes are connected; there are no orphan or isolated nodes.
    - **LT_4 (20 pts):** Confirm that node IDs are unique and appear in ascending order.
    - **LT_5 (20 pts):** Ensure that at least one valid path exists from the start to the end node.
    - **LT_6 (20 pts):** Validate that all node types are from the allowed set (Start, End, Process, Decision).
    - **LT_7 (20 pts):** If loops exist, check that each has a proper termination condition.
    - **LT_8 (10 pts):** All nodes must have clear, non-empty, meaningful labels.
    - **LT_9 (20 pts):** Each decision node must have exactly two outgoing edges (e.g., Yes/No).

    ---

    ### Practical Reasoning Checks

    - **PT_1 (20 pts):** Generate and evaluate the flowchart against a simple school-level test case.
    - **PT_2 (20 pts):** Generate and evaluate a second test case for consistency.

    ---

    ### Additional Checks (Only if \`use_professional_checks = true\`)

    - **PT_3 (20 pts):** Test the flowchart against an edge or boundary case. Does it handle unexpected or unusual input?
    - **PT_4 (10 pts):** Assess the logical efficiency of the flowchart — does it solve the problem with minimal, necessary steps?

    ---

    ### Output Format (Plain Text)

    For each check, report:

    - The check name (e.g., LT_1: Start and End Node Check)
    - The score (e.g., 30/30)
    - A short explanation (e.g., "Exactly one start and one end node found.")

    Finally, provide:

    - The **total score** before normalization
    - The **normalized score out of 100**
    - A **final comment** summarizing the quality of the flowchart

    Now, evaluate the provided flowchart image and produce the report.
    `;

    const requestBody = {
      model: 'llama3.2-vision',
      messages: [
        {
          role: 'user',
          content: FLOWCHART_EVALUATION_PROMPT,
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