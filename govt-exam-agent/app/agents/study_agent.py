from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService


class StudyAgent:
    def __init__(self):
        self.llm = LLMService()
        self.memory = MemoryService()
        self.rag = RAGService()
        
        # Build the LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph_builder = StateGraph(AgentState)
        
        # Add nodes for each step
        graph_builder.add_node("store_memory", self._store_memory)
        graph_builder.add_node("detect_intent", self._detect_intent)
        graph_builder.add_node("retrieve_context", self._retrieve_context)
        graph_builder.add_node("create_prompt", self._create_prompt)
        graph_builder.add_node("call_llm", self._call_llm)
        graph_builder.add_node("save_response", self._save_response)
        
        # Connect nodes in sequence
        graph_builder.add_edge(START, "store_memory")
        graph_builder.add_edge("store_memory", "detect_intent")
        graph_builder.add_edge("detect_intent", "retrieve_context")
        graph_builder.add_edge("retrieve_context", "create_prompt")
        graph_builder.add_edge("create_prompt", "call_llm")
        graph_builder.add_edge("call_llm", "save_response")
        graph_builder.add_edge("save_response", END)
        
        return graph_builder.compile()
    
    def _store_memory(self, state: AgentState) -> AgentState:
        """Node 1: Store user query in memory"""
        self.memory.update(state["session_id"], "user", state["query"])
        state["history"] = self.memory.get(state["session_id"])
        state["error"] = False
        return state
    
    def _detect_intent(self, state: AgentState) -> AgentState:
        """Node 2: Detect user intent"""
        query = state["query"].lower()
        
        if "mcq" in query or "quiz" in query or "test" in query:
            state["intent"] = "MCQ"
        elif "explain" in query or "what is" in query or "define" in query:
            state["intent"] = "STUDY"
        else:
            state["intent"] = "GENERAL"
        
        return state
    
    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Node 3: Retrieve relevant documents using RAG"""
        context_docs = self.rag.retrieve(
            f"List all projects or relevant items: {state['query']}",
            session_id=state["session_id"]
        )
        state["context"] = "\n".join(context_docs) if context_docs else ""
        return state
    
    def _create_prompt(self, state: AgentState) -> AgentState:
        """Node 4: Create system prompt based on context and intent"""
        if state["context"]:
            system_prompt = (
                "You are a helpful assistant.\n"
                "Extract ALL relevant projects from the context.\n"
                "List every project clearly; do not skip any.\n"
                "Answer ONLY using the provided document context."
            )
        else:
            if state["intent"] == "STUDY":
                system_prompt = (
                    "You are a helpful teacher. Explain clearly step by step. "
                    "Use previous conversation context if needed."
                )
            elif state["intent"] == "MCQ":
                system_prompt = (
                    "Generate 3 multiple choice questions with 4 options and answers. "
                    "Use previous context if needed."
                )
            else:
                system_prompt = "You are a helpful assistant."
        
        state["system_prompt"] = system_prompt
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        if state["context"]:
            messages.append({"role": "system", "content": f"Context:\n{state['context']}"})
        messages.extend(state["history"])
        
        state["messages"] = messages
        return state
    
    def _call_llm(self, state: AgentState) -> AgentState:
        """Node 5: Call LLM to generate response"""
        response = self.llm.generate(state["messages"])
        
        if response == "ERROR":
            state["error"] = True
            state["response"] = "Something went wrong"
            state["response_type"] = "error"
        else:
            state["error"] = False
            state["response"] = response
            state["response_type"] = "rag" if state["context"] else state["intent"].lower()
        
        return state
    
    def _save_response(self, state: AgentState) -> AgentState:
        """Node 6: Save assistant response to memory"""
        if not state["error"]:
            self.memory.update(state["session_id"], "assistant", state["response"])
        return state
    
    def handle(self, session_id: str, query: str):
        """Execute the workflow"""
        # Initialize state
        initial_state = {
            "session_id": session_id,
            "query": query,
            "history": [],
            "intent": "",
            "context": "",
            "system_prompt": "",
            "messages": [],
            "response": "",
            "response_type": "",
            "error": False,
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return result
        if final_state["error"]:
            return {
                "type": "error",
                "content": "Something went wrong",
                "follow_up": "Please try again"
            }
        else:
            return {
                "type": final_state["response_type"],
                "content": final_state["response"]
            }