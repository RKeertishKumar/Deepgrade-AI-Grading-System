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
      model: 'llama3.2-vision',
      messages: [
        {
          role: 'user',
          content: 'Analyze this image and Grade it Out of 10',
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