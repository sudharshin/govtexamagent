import {
  Component,
  Input,
  ViewChild,
  ElementRef,
  AfterViewChecked
} from '@angular/core';

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

  @ViewChild('messagesArea') messagesArea!: ElementRef;
  @ViewChild('bottomAnchor') bottomAnchor!: ElementRef;

  userInput: string = '';
  private lastMessageCount = 0;
  private lastLoadingState = false;

  sendMessage() {
    if (this.userInput.trim()) {
      this.onSendMessage(this.userInput);
      this.userInput = '';
    }
  }

  ngAfterViewChecked() {
    if (
      this.messages.length > this.lastMessageCount ||
      (this.lastLoadingState && !this.loading)
    ) {
      this.scrollToBottom();
      this.lastMessageCount = this.messages.length;
    }

    this.lastLoadingState = this.loading;
  }

  private scrollToBottom() {
    requestAnimationFrame(() => {
      this.bottomAnchor?.nativeElement.scrollIntoView({
        behavior: 'smooth'
      });
    });
  }

  trackByMessageId(index: number, message: ChatMessage) {
    return message.id;
  }
}