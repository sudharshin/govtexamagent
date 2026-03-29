import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { ResponseFormatterService, ChatMessage } from '../../services/response-formatter.service';

@Component({
  selector: 'app-previous-year-questions',
  templateUrl: './previous-year-questions.component.html',
  styleUrls: ['./previous-year-questions.component.css']
})
export class PreviousYearQuestionsComponent implements OnInit, OnDestroy {
  @Input() sessionId: string = '';

  messages: ChatMessage[] = [];
  loading: boolean = false;
  selectedYear: string = '';
  years: string[] = ['2023', '2022', '2021', '2020', '2019'];
  private sessionStorageKey = '';

  constructor(private formatter: ResponseFormatterService) {}

  ngOnInit() {
    this.sessionStorageKey = `prev-year-${this.sessionId}`;
    const savedMessages = sessionStorage.getItem(this.sessionStorageKey);
    if (savedMessages) {
      this.messages = JSON.parse(savedMessages);
    } else {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '📝 Welcome to Previous Year Questions! Select a year or ask for specific questions from past exams.'
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

  onYearSelected(year: string) {
    this.selectedYear = year;
    this.messages.push(this.formatter.createChatMessage('user', `Show me questions from ${year}`));
    this.loading = true;

    // Simulated response (backend hook pending)
    setTimeout(() => {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          `📚 Here are featured questions from ${year}:\n\n1. Define LCM and HCF with examples\n2. Solve: Find LCM(24, 36)\n3. Real-world application question\n\nWould you like to practice these?`
        )
      );
      this.loading = false;
      this.saveMessages();
    }, 1000);
  }

  onSendMessage(message: string) {
    if (!message.trim()) return;

    this.messages.push(this.formatter.createChatMessage('user', message));
    this.loading = true;

    setTimeout(() => {
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '✅ Found 5 relevant questions matching your search. Would you like to attempt them as a test?'
        )
      );
      this.loading = false;
      this.saveMessages();
    }, 1000);
  }

  clearChat() {
    this.messages = [];
    this.selectedYear = '';
    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '📝 Chat cleared. Select a year to see previous year questions.'
      )
    );
    this.saveMessages();
  }
}
