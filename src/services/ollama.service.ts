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
      `You are an expert in evaluating flowcharts from images.

Analyze the attached flowchart image. Perform the following STRUCTURAL CHECKS (Total: 100 pts):
- **S1 (20 pts):** Exactly one Start and one End node.
- **S2 (15 pts):** All node IDs are unique and sequential.
- **S3 (15 pts):** All node types are valid (Start, End, Process, Decision).
- **S4 (15 pts):** All nodes are connected; no isolated nodes.
- **S5 (10 pts):** All Decision nodes have two outgoing edges (e.g., Yes/No).
- **S6 (10 pts):** Clear, meaningful labels on each node.
- **S7 (15 pts):** At least one complete path from Start to End.

### OUTPUT FORMAT (JSON only, no explanation outside JSON)
Return the result as a JSON object like this:

{
  "S1": { "name": "Start-End Node Check", "score": "20/20", "reason": "Exactly one Start and one End node." },
  "S2": { "name": "Unique Sequential Node IDs Check", "score": "15/15", "reason": "All node IDs are unique and sequential." },
  "S3": { "name": "Valid Node Types Check", "score": "15/15", "reason": "All node types are valid." },
  "S4": { "name": "Connected Nodes Check", "score": "15/15", "reason": "All nodes are connected." },
  "S5": { "name": "Decision Node Outgoing Edges Check", "score": "10/10", "reason": "Each Decision node has two outgoing edges." },
  "S6": { "name": "Clear Labels Check", "score": "10/10", "reason": "Each node has clear and meaningful labels." },
  "S7": { "name": "Complete Path from Start to End Check", "score": "15/15", "reason": "There is at least one complete path from Start to End." },
  "totalScore": 100,
  "finalComment": "Excellent flowchart quality with all structural criteria met."
}

Respond only with the JSON object.`;  // Closing backtick here

    const requestBody = {
      model: 'llama3.2-vision',
      options:{'temperature':0.2},
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