import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ResponseService {
    private responseText: string = '';
  
    setResponse(response: string) {
      this.responseText = response;
    }
  
    getResponse(): string {
      return this.responseText;
    }
  }