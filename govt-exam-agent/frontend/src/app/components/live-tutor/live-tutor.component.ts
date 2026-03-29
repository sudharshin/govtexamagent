import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ResponseFormatterService, ChatMessage } from '../../services/response-formatter.service';

@Component({
  selector: 'app-live-tutor',
  templateUrl: './live-tutor.component.html',
  styleUrls: ['./live-tutor.component.css']
})
export class LiveTutorComponent implements OnInit, OnDestroy {
  @Input() sessionId: string = '';

  messages: ChatMessage[] = [];
  loading: boolean = false;
  uploadedFileName: string = '';
  hasUploadedDocument: boolean = false;
  private sessionStorageKey = '';

  constructor(
    private api: ApiService,
    private formatter: ResponseFormatterService
  ) {}

  ngOnInit() {
    this.sessionStorageKey = `live-tutor-${this.sessionId}`;
    // Load messages from sessionStorage if available
    const savedMessages = sessionStorage.getItem(this.sessionStorageKey);
    if (savedMessages) {
      this.messages = JSON.parse(savedMessages);
    } else {
      // Initialize with welcome message
      this.messages.push(
        this.formatter.createChatMessage(
          'assistant',
          '👋 Welcome to Live Tutor! Upload a PDF or ask any question about your studies. I\'m here to help clarify concepts and answer your doubts.'
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

  onSendMessage(query: string) {
    if (!query.trim()) return;

    // Add user message
    this.messages.push(this.formatter.createChatMessage('user', query));
    this.loading = true;

    this.api.study(this.sessionId, query, this.hasUploadedDocument).subscribe({
      next: (response) => {
        const formattedResponse = this.formatter.formatStudyResponse(response);
        this.messages.push(
          this.formatter.createChatMessage('assistant', formattedResponse, response)
        );
        this.loading = false;
        this.saveMessages();
      },
      error: (err) => {
        const errorMsg = err.message || 'Failed to get response. Please try again.';
        this.messages.push(
          this.formatter.createChatMessage('error', `⚠️ ${errorMsg}`)
        );
        this.loading = false;
        this.saveMessages();
      }
    });
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      this.messages.push(
        this.formatter.createChatMessage('error', '❌ Please upload a PDF file only.')
      );
      this.saveMessages();
      return;
    }

    this.loading = true;
    this.api.upload(this.sessionId, file).subscribe({
      next: (response) => {
        this.uploadedFileName = file.name;
        this.hasUploadedDocument = true;
        this.messages.push(
          this.formatter.createChatMessage(
            'assistant',
            `✅ Successfully uploaded "${file.name}". I can now use this for answering your questions!\n\n📌 Note: I will prioritize answers from this document. If your question is not covered in the document, I'll provide general knowledge from my training.`
          )
        );
        this.loading = false;
        this.saveMessages();
        // Reset file input
        event.target.value = '';
      },
      error: (err) => {
        const errorMsg = err.message || 'Upload failed. Please try again.';
        this.messages.push(
          this.formatter.createChatMessage('error', `❌ Upload Error: ${errorMsg}`)
        );
        this.loading = false;
        this.saveMessages();
        event.target.value = '';
      }
    });
  }

  clearChat() {
    this.messages = [];
    this.messages.push(
      this.formatter.createChatMessage(
        'assistant',
        '🔄 Chat cleared. What would you like to know?'
      )
    );
    this.saveMessages();
  }
}
