"""AgentState definition for LangGraph workflow."""
from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    """State shared across all agents in the workflow.
    
    This state is passed between LangGraph nodes and modified by each agent.
    """
    # Input data
    input_data: Any  # Can be dict or string
    
    # Parsed product data
    parsed_data: Optional[Dict[str, Any]]
    
    # Description output
    description: Optional[Dict[str, Any]]
    
    # Comparison output
    similar_products: Optional[List[Dict[str, Any]]]
    comparison: Optional[Dict[str, Any]]
    
    # FAQ output
    faqs: Optional[List[Dict[str, Any]]]
    
    # Operations to perform
    operations: List[str]
    
    # Error tracking
    error: Optional[str]
