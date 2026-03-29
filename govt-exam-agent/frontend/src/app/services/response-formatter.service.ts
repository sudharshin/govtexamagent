import { Injectable } from '@angular/core';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'error';
  content: string;
  timestamp: Date;
  metadata?: any;
}

@Injectable({ providedIn: 'root' })
export class ResponseFormatterService {
  
  formatStudyResponse(response: any): string {
    try {
      if (response.error) {
        return `❌ Error: ${response.error}`;
      }
      if (response.content) {
        return response.content;
      }
      return JSON.stringify(response);
    } catch (e) {
      return 'Error formatting response';
    }
  }

  formatMcqResponse(response: any): any {
    try {
      if (response.error) {
        return { error: response.error, questions: [] };
      }
      if (response.content && typeof response.content === 'string') {
        const parsed = JSON.parse(response.content);
        return parsed;
      }
      return response.content || response;
    } catch (e) {
      return { error: 'Failed to parse MCQ response', questions: [] };
    }
  }

  formatMcqForDisplay(mcqData: any): { topic: string; questions: any[] } {
    if (!mcqData) return { topic: '', questions: [] };
    return {
      topic: mcqData.topic || 'Questions',
      questions: mcqData.questions || []
    };
  }

  createChatMessage(type: 'user' | 'assistant' | 'error', content: string, metadata?: any): ChatMessage {
    return {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      metadata
    };
  }
}
