import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../../services/api.service';
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
  selectedExam: string = '';

  years: string[] = ['2023', '2022', '2021', '2020', '2019'];

  pdfs: any[] = [];
  questions: any[] = [];

  private sessionStorageKey = '';

  constructor(
    private formatter: ResponseFormatterService,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.sessionStorageKey = `prev-year-${this.sessionId}`;

    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '📝 Enter exam name (e.g., SSC CGL, TNPSC, RRB) or select a year.'
      )
    );
  }

  onSendMessage(message: string) {
    if (!message.trim()) return;

    this.selectedExam = message;

    this.messages.push(this.formatter.createChatMessage('user', message));
    this.fetchPYQs(message);
  }

  onYearSelected(year: string) {
    this.selectedYear = year;

    if (!this.selectedExam) {
      this.messages.push(
        this.formatter.createChatMessage('error', '⚠️ Please enter exam name first')
      );
      return;
    }

    const query = `${this.selectedExam} ${year}`;

    this.messages.push(
      this.formatter.createChatMessage('user', `📅 ${query}`)
    );

    this.fetchPYQs(query);
  }

  fetchPYQs(query: string) {
    this.loading = true;

    this.api.pyqs(query).subscribe({
      next: (res) => {
        this.pdfs = res.pdfs || [];
        this.questions = res.web_questions || [];

        this.messages.push(
          this.formatter.createChatMessage(
            'assistant',
            `✅ Found ${this.pdfs.length} PDFs and ${this.questions.length} question sets`
          )
        );

        this.loading = false;
      },
      error: () => {
        this.messages.push(
          this.formatter.createChatMessage('error', '❌ Failed to fetch PYQs')
        );
        this.loading = false;
      }
    });
  }

  clearChat() {
    this.messages = [];
    this.pdfs = [];
    this.questions = [];
    this.selectedYear = '';
    this.selectedExam = '';

    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '📝 Chat cleared. Enter exam name again.'
      )
    );
  }

  ngOnDestroy() {}
}