import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  activeAgent: string = 'live-tutor';
  sessionId = this._generateSessionId();

  constructor() {}

  private _generateSessionId(): string {
    return 's_' + Math.random().toString(36).substring(2, 12);
  }

  setAgent(agent: string) {
    this.activeAgent = agent;
  }
}
