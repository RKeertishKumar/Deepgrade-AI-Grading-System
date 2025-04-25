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
    // Use the user's question if provided, otherwise use the default flowchart prompt
    const prompt = userQuestion.trim() !== '' ? 
      userQuestion : 
      `You are an expert in evaluating flowcharts from images.

Analyze the attached flowchart image. Perform the following checks:

### STRUCTURAL CHECKS (Total: 100 pts)
- **S1 (20 pts):** Exactly one Start and one End node.
- **S2 (15 pts):** All node IDs are unique and sequential.
- **S3 (15 pts):** All node types are valid (Start, End, Process, Decision).
- **S4 (15 pts):** All nodes are connected; no isolated nodes.
- **S5 (10 pts):** All Decision nodes have two outgoing edges (e.g., Yes/No).
- **S6 (10 pts):** Clear, meaningful labels on each node.
- **S7 (15 pts):** At least one complete path from Start to End.

### OUTPUT FORMAT (Plain Text)
For each check:
- Check code and name (e.g., S1: Start-End Node Check)
- Score (e.g., 20/20)
- One-line reason

Then output:
- Total score out of 100
- Final comment on the flowchart's quality

Be concise and accurate. Assume professional use.`;

    const requestBody = {
      model: 'llama3.2-vision',
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