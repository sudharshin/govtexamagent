import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ResponseFormatterService } from '../../services/response-formatter.service';

interface MCQQuestion {
  question_id: number;
  question_text: string;
  options: { option_letter: string; text: string }[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
}

@Component({
  selector: 'app-mcq-agent',
  templateUrl: './mcq-agent.component.html',
  styleUrls: ['./mcq-agent.component.css']
})
export class McqAgentComponent implements OnInit, OnDestroy {
  @Input() sessionId: string = '';

  topic: string = '';
  numQuestions: number = 10;
  loading: boolean = false;
  questions: MCQQuestion[] = [];
  userAnswers: { [key: number]: string } = {};
  submitted: boolean = false;
  score: number = 0;
  private sessionStorageKey = '';

  constructor(
    private api: ApiService,
    private formatter: ResponseFormatterService
  ) {}

  ngOnInit() {
    this.sessionStorageKey = `mcq-${this.sessionId}`;
    // Load MCQ state from sessionStorage if available
    const savedState = sessionStorage.getItem(this.sessionStorageKey);
    if (savedState) {
      const state = JSON.parse(savedState);
      this.topic = state.topic || '';
      this.questions = state.questions || [];
      this.userAnswers = state.userAnswers || {};
      this.submitted = state.submitted || false;
      this.score = state.score || 0;
    }
  }

  ngOnDestroy() {
    this.saveMCQState();
  }

  private saveMCQState() {
    const state = {
      topic: this.topic,
      questions: this.questions,
      userAnswers: this.userAnswers,
      submitted: this.submitted,
      score: this.score
    };
    sessionStorage.setItem(this.sessionStorageKey, JSON.stringify(state));
  }

  getAnsweredCount(): number {
    return Object.keys(this.userAnswers).length;
  }

  generateMcq() {
    if (!this.topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    this.loading = true;
    this.questions = [];
    this.userAnswers = {};
    this.submitted = false;

    this.api.mcq(this.sessionId, this.topic.trim(), this.numQuestions).subscribe({
      next: (response) => {
        const mcqData = this.formatter.formatMcqResponse(response);
        if (mcqData && mcqData.questions && Array.isArray(mcqData.questions)) {
          this.questions = mcqData.questions;
          this.saveMCQState();
        } else {
          alert('Failed to parse MCQ response');
        }
        this.loading = false;
      },
      error: (err) => {
        alert('Error generating MCQs: ' + (err.message || 'Unknown error'));
        this.loading = false;
      }
    });
  }

  selectAnswer(questionId: number, answer: string) {
    if (!this.submitted) {
      this.userAnswers[questionId] = answer;
      this.saveMCQState();
    }
  }

  submitAnswers() {
    const answeredCount = Object.keys(this.userAnswers).length;
    if (answeredCount < this.questions.length) {
      alert(`Please answer all questions before submitting. You have answered ${answeredCount} out of ${this.questions.length}`);
      return;
    }

    this.submitted = true;
    this.calculateScore();
  }

  calculateScore() {
    let correct = 0;
    this.questions.forEach(q => {
      if (this.userAnswers[q.question_id] === q.correct_answer) {
        correct++;
      }
    });
    this.score = Math.round((correct / this.questions.length) * 100);
  }

  resetTest() {
    this.questions = [];
    this.userAnswers = {};
    this.submitted = false;
    this.score = 0;
    this.topic = '';
    this.saveMCQState();
  }

  getDifficultyColor(difficulty: string): string {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return '#4caf50';
      case 'medium':
        return '#ff9800';
      case 'hard':
        return '#f44336';
      default:
        return '#999';
    }
  }
}
