import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ResponseFormatterService, ChatMessage } from '../../services/response-formatter.service';

@Component({
  selector: 'app-planner-agent',
  templateUrl: './planner-agent.component.html',
  styleUrls: ['./planner-agent.component.css']
})
export class PlannerAgentComponent implements OnInit, OnDestroy {

  @Input() sessionId: string = '';

  messages: ChatMessage[] = [];
  loading: boolean = false;
  private sessionStorageKey = '';

  constructor(
    private formatter: ResponseFormatterService,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.sessionStorageKey = `planner-agent-${this.sessionId}`;
    const savedMessages = sessionStorage.getItem(this.sessionStorageKey);

    if (savedMessages) {
      this.messages = JSON.parse(savedMessages);
    } else {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '📅 Tell me your exam (e.g., "Bank PO", "UPSC", "TNPSC Group 2") and I will create a structured study plan for you.'
        )
      );
      this.saveMessages();
    }
  }

  ngOnDestroy() {
    this.saveMessages();
  }

  private saveMessages() {
    sessionStorage.setItem(this.sessionStorageKey, JSON.stringify(this.messages));
  }

  onSendMessage(message: string) {
    if (!message.trim()) return;

    this.messages.push(this.formatter.createChatMessage('user', message));
    this.loading = true;

    this.api.planner(this.sessionId, message).subscribe({
      next: (res) => {
        const formatted = this.formatPlan(res.plan);
        this.messages.push(
          this.formatter.createChatMessage('assistant', formatted)
        );
        this.loading = false;
        this.saveMessages();
      },
      error: () => {
        this.messages.push(
          this.formatter.createChatMessage('error', '❌ Failed to generate plan')
        );
        this.loading = false;
      }
    });
  }

  // 🔥 Format plan into clean UI-friendly structure
  formatPlan(plan: string): string {

  return `
📚 STUDY PLAN

${plan
  .replace(/Month/g, '\n\n📅 Month')
  .replace(/1\./g, '\n\n📌 1.')
  .replace(/2\./g, '\n\n📌 2.')
  .replace(/3\./g, '\n\n📌 3.')
  .replace(/4\./g, '\n\n📌 4.')
  .replace(/5\./g, '\n\n📌 5.')
  .replace(/6\./g, '\n\n📌 6.')
  .replace(/7\./g, '\n\n📌 7.')
  .replace(/8\./g, '\n\n📌 8.')
}
`;
}

  clearChat() {
    this.messages = [];
    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '📅 Chat cleared. Tell me your exam again.'
      )
    );
    this.saveMessages();
  }
}