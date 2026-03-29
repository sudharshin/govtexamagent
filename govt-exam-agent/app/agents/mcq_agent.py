from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.services.mcq_service import MCQService


class MCQAgent:
    """Agent specialized for generating multiple choice questions"""
    
    def __init__(self):
        self.llm = LLMService()
        self.memory = MemoryService()
        self.rag = RAGService()
        self.mcq = MCQService()
        
        # Build the LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow for MCQ generation"""
        graph_builder = StateGraph(AgentState)
        
        # Add nodes for MCQ generation workflow
        graph_builder.add_node("store_memory", self._store_memory)
        graph_builder.add_node("retrieve_context", self._retrieve_context)
        graph_builder.add_node("create_prompt", self._create_prompt)
        graph_builder.add_node("call_llm", self._call_llm)
        graph_builder.add_node("parse_mcq", self._parse_mcq)
        graph_builder.add_node("save_response", self._save_response)
        
        # Connect nodes in sequence
        graph_builder.add_edge(START, "store_memory")
        graph_builder.add_edge("store_memory", "retrieve_context")
        graph_builder.add_edge("retrieve_context", "create_prompt")
        graph_builder.add_edge("create_prompt", "call_llm")
        graph_builder.add_edge("call_llm", "parse_mcq")
        graph_builder.add_edge("parse_mcq", "save_response")
        graph_builder.add_edge("save_response", END)
        
        return graph_builder.compile()
    
    def _store_memory(self, state: AgentState) -> AgentState:
        """Node 1: Store user query in memory"""
        self.memory.update(state["session_id"], "user", state["query"])
        state["history"] = self.memory.get(state["session_id"])
        state["error"] = False
        state["intent"] = "MCQ"
        return state
    
    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Node 2: Retrieve relevant documents from uploaded PDFs (if any)"""
        context_docs = self.rag.retrieve(
            state["query"],
            session_id=state["session_id"]
        )
        state["context"] = "\n".join(context_docs) if context_docs else ""
        return state
    
    def _create_prompt(self, state: AgentState) -> AgentState:
        """Node 3: Create MCQ-specific system prompt"""
        system_prompt = (
            "You are an expert MCQ question generator for government exams.\n"
            "Generate high-quality multiple choice questions with the following JSON format:\n"
            "{\n"
            '  "questions": [\n'
            "    {\n"
            '      "question": "The question text here",\n'
            '      "options": [\n'
            '        {"letter": "A", "text": "Option A text"},\n'
            '        {"letter": "B", "text": "Option B text"},\n'
            '        {"letter": "C", "text": "Option C text"},\n'
            '        {"letter": "D", "text": "Option D text"}\n'
            "      ],\n"
            '      "correct_answer": "A",\n'
            '      "explanation": "Detailed explanation of why this is correct...",\n'
            '      "difficulty": "medium"\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Return ONLY the JSON, no other text.\n"
            "Ensure questions are clear, options are distinct, and explanations are detailed."
        )
        
        state["system_prompt"] = system_prompt
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        if state["context"]:
            messages.append({
                "role": "system",
                "content": f"Generate MCQs based on this content:\n{state['context']}"
            })
        
        messages.extend(state["history"])
        state["messages"] = messages
        return state
    
    def _call_llm(self, state: AgentState) -> AgentState:
        """Node 4: Call LLM to generate MCQ JSON"""
        response = self.llm.generate(state["messages"])
        
        if response == "ERROR":
            state["error"] = True
            state["response"] = "Failed to generate MCQs"
            state["response_type"] = "error"
        else:
            state["error"] = False
            state["response"] = response  # Raw LLM response (should be JSON)
            state["response_type"] = "mcq_raw"
        
        return state
    
    def _parse_mcq(self, state: AgentState) -> AgentState:
        """Node 5: Parse raw LLM response into structured MCQ format"""
        if state["error"]:
            return state
        
        try:
            mcq_response = self.mcq.parse_llm_response_to_mcq(state["response"])
            state["response"] = mcq_response.model_dump_json()  # Convert to JSON string
            state["response_type"] = "mcq"
        except Exception as e:
            print(f"MCQ parsing error: {e}")
            state["error"] = True
            state["response_type"] = "error"
            state["response"] = f"Failed to parse MCQ: {str(e)}"
        
        return state
    
    def _save_response(self, state: AgentState) -> AgentState:
        """Node 6: Save MCQ generation to memory"""
        if not state["error"]:
            # Save as assistant response
            self.memory.update(
                state["session_id"],
                "assistant",
                f"[MCQ Generated: {len(state.get('response', ''))} chars]"
            )
        return state
    
    def handle(self, session_id: str, topic: str = None, num_questions: int = 3):
        """
        Execute MCQ generation workflow
        
        Args:
            session_id: Unique conversation identifier
            topic: Optional topic for MCQ generation
            num_questions: Number of questions to generate
        """
        # Build query
        if topic:
            query = f"Generate {num_questions} MCQs about: {topic}"
        else:
            query = f"Generate {num_questions} MCQs based on the uploaded document"
        
        # Initialize state
        initial_state = {
            "session_id": session_id,
            "query": query,
            "history": [],
            "intent": "MCQ",
            "context": "",
            "system_prompt": "",
            "messages": [],
            "response": "",
            "response_type": "",
            "error": False,
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return structured response
        if final_state["error"]:
            return {
                "type": "error",
                "content": final_state["response"],
                "session_id": session_id
            }
        else:
            import json
            try:
                mcq_data = json.loads(final_state["response"])
            except:
                mcq_data = final_state["response"]
            
            return {
                "type": "mcq",
                "content": mcq_data,
                "session_id": session_id
            }
