import { Component, Input, OnInit, OnDestroy } from '@angular/core';
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

  constructor(private formatter: ResponseFormatterService) {}

  ngOnInit() {
    this.sessionStorageKey = `planner-agent-${this.sessionId}`;
    const savedMessages = sessionStorage.getItem(this.sessionStorageKey);
    if (savedMessages) {
      this.messages = JSON.parse(savedMessages);
    } else {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '📅 Welcome to Study Planner! Tell me about your exam and goals, and I\'ll create a personalized study plan for you.'
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

    // Simulated response (backend hook pending)
    setTimeout(() => {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '✅ I\'ve created a study plan based on your requirements:\n\n📌 Phase 1: Fundamentals (Week 1-2)\n📌 Phase 2: Practice (Week 3-4)\n📌 Phase 3: Mock Tests (Week 5)\n\nWould you like adjustments?'
        )
      );
      this.loading = false;
      this.saveMessages();
    }, 1000);
  }

  clearChat() {
    this.messages = [];
    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '📅 Chat cleared. Tell me about your exam preparation needs.'
      )
    );
    this.saveMessages();
  }
}
