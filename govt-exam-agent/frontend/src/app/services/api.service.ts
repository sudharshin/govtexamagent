import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

const API_BASE = environment.apiBase;

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  study(sessionId: string, query: string, hasDocument: boolean = false): Observable<any> {
    return this.http.post(`${API_BASE}/study`, { 
      session_id: sessionId, 
      query,
      has_document: hasDocument
    });
  }

  mcq(sessionId: string, topic: string, num_questions: number): Observable<any> {
    return this.http.post(`${API_BASE}/mcq`, { 
      session_id: sessionId, 
      topic, 
      num_questions 
    });
  }

  upload(sessionId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    return this.http.post(`${API_BASE}/upload?session_id=${sessionId}`, formData);
  }
  planner(sessionId: string, exam: string): Observable<any> {
      return this.http.post(`${API_BASE}/planner`, {
        session_id: sessionId,
        exam
      });
  }
  pyqs(exam: string): Observable<any> {
  return this.http.get(`${API_BASE}/pyqs`, {
    params: { exam }
  });
}
}
