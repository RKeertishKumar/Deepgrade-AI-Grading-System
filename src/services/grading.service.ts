import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GradingService {
  private apiUrl = 'http://localhost:5000/api/grade';

  constructor(private http: HttpClient) {}

  gradeResponse(response: string): Observable<any> {
    return this.http.post(this.apiUrl, { response });
  }

  getPreviousResponses(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/responses`);
  }
}