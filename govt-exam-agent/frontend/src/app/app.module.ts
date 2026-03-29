import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { LiveTutorComponent } from './components/live-tutor/live-tutor.component';
import { McqAgentComponent } from './components/mcq-agent/mcq-agent.component';
import { PlannerAgentComponent } from './components/planner-agent/planner-agent.component';
import { PreviousYearQuestionsComponent } from './components/previous-year-questions/previous-year-questions.component';
import { ChatInterfaceComponent } from './components/chat-interface/chat-interface.component';

@NgModule({
  declarations: [
    AppComponent,
    LiveTutorComponent,
    McqAgentComponent,
    PlannerAgentComponent,
    PreviousYearQuestionsComponent,
    ChatInterfaceComponent
  ],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
