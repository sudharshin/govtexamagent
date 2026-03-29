from typing import TypedDict


class AgentState(TypedDict):
    """
    Unified state schema for all agents using LangGraph.
    This state is passed through the entire workflow graph.
    """
    # Input
    session_id: str          # Unique conversation identifier
    query: str               # User's input query
    
    # Processing steps
    history: list            # Conversation history
    intent: str              # Detected intent (MCQ, STUDY, GENERAL)
    context: str             # Retrieved document context from RAG
    system_prompt: str       # Generated system prompt for LLM
    messages: list           # Final messages to send to LLM
    
    # Output
    response: str            # LLM response
    response_type: str       # Response type (rag, study, mcq, general, error)
    error: bool              # Whether an error occurred
