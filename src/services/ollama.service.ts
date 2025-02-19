import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OllamaService {
  private apiUrl = 'http://localhost:11434/api/chat'; 

  constructor(private http: HttpClient) {}

  sendImageToOllama(imageBase64: string): Observable<any> {
    const requestBody = {
      model: 'llama3.2-vision',
      messages: [
        {
          role: 'user',
          content: 'Analyze this?',
          images: [imageBase64] 
        }
      ]
    };
    return this.http.post<any>(this.apiUrl, requestBody);
  }
}
