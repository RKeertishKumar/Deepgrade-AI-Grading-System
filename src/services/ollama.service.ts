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
    const requestBody = {
      model: 'granite3.2-vision',
      messages: [
      {
        role: 'user',
        content: `You are a grader assistant. Analyze the following image of a student's answer.

  Your job is to describe their answer in plain text, using words and phrases that match the following grading criteria. Do not add any scores or formatting. Just describe the content naturally, using keywords that match these areas:

  1. **Correct Algorithm**: Use phrases like “correct algorithm”, “proper steps”, or “accurate logic”.
  2. **Flowchart Structure**: Mention terms like “begin”, “start”, “end”, “terminator”, “decision”, or “process”.
  3. **Variable Usage**: Include words like “variable”, “declare”, “initialize”, or “assign”.
  4. **Loop Logic**: Mention terms like “while”, “for”, “loop”, “repeat”, or “until”.
  5. **Output Mention**: Include phrases like “output”, “print”, “display”, or “result”.

  Be concise but ensure all matched criteria appear explicitly. Return only the plain text response.`,
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