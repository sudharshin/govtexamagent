import { Component, Input, ViewChild, ElementRef, AfterViewChecked, ChangeDetectorRef } from '@angular/core';
import { ChatMessage } from '../../services/response-formatter.service';

@Component({
  selector: 'app-chat-interface',
  templateUrl: './chat-interface.component.html',
  styleUrls: ['./chat-interface.component.css']
})
export class ChatInterfaceComponent implements AfterViewChecked {
  @Input() messages: ChatMessage[] = [];
  @Input() loading: boolean = false;
  @Input() placeholder: string = 'Type your question...';
  @Input() onSendMessage: (message: string) => void = () => {};

  @ViewChild('messagesArea') private messagesArea!: ElementRef<HTMLDivElement>;
  
  userInput: string = '';
  private lastMessageCount = 0;
  private lastLoadingState = false;

  constructor(private cdr: ChangeDetectorRef) {}

  sendMessage() {
    if (this.userInput.trim()) {
      this.onSendMessage(this.userInput);
      this.userInput = '';
    }
  }

  ngAfterViewChecked() {
    // Scroll when new messages are added or loading completes
    if (this.messages.length > this.lastMessageCount || 
        (this.lastLoadingState && !this.loading)) {
      this.scrollToBottom();
      this.lastMessageCount = this.messages.length;
    }
    this.lastLoadingState = this.loading;
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesArea && this.messagesArea.nativeElement) {
        setTimeout(() => {
          const element = this.messagesArea.nativeElement;
          if (element) {
            element.scrollTop = element.scrollHeight;
          }
        }, 0);
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  trackByMessageId(index: number, message: ChatMessage) {
    return message.id;
  }
}
