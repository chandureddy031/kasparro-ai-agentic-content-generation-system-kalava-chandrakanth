"""LangGraph workflow definition.

This module defines the StateGraph that orchestrates all agents using LangGraph.
"""
import logging
from typing import List
from langgraph.graph import StateGraph, END

from models.state import AgentState
from graph.nodes import parser_node, description_node, faq_node, comparison_node

logger = logging.getLogger(__name__)


def should_run_description(state: AgentState) -> str:
    """Conditional edge: check if description should run.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    operations = state.get('operations', [])
    if 'description' in operations:
        return 'description'
    return 'check_comparison'


def should_run_comparison(state: AgentState) -> str:
    """Conditional edge: check if comparison should run.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    operations = state.get('operations', [])
    if 'comparison' in operations:
        return 'comparison'
    return 'check_faq'


def should_run_faq(state: AgentState) -> str:
    """Conditional edge: check if FAQ should run.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    operations = state.get('operations', [])
    if 'faq' in operations:
        return 'faq'
    return END


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow.
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create StateGraph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parser", parser_node)
    workflow.add_node("description", description_node)
    workflow.add_node("comparison", comparison_node)
    workflow.add_node("faq", faq_node)
    
    # Set entry point
    workflow.set_entry_point("parser")
    
    # Add conditional edges from parser
    workflow.add_conditional_edges(
        "parser",
        should_run_description,
        {
            "description": "description",
            "check_comparison": "check_comparison"
        }
    )
    
    # Add check_comparison as a conditional node
    workflow.add_conditional_edges(
        "check_comparison",
        should_run_comparison,
        {
            "comparison": "comparison",
            "check_faq": "check_faq"
        }
    )
    
    # Add check_faq as a conditional node
    workflow.add_conditional_edges(
        "check_faq",
        should_run_faq,
        {
            "faq": "faq",
            END: END
        }
    )
    
    # Connect description -> check_comparison
    workflow.add_edge("description", "check_comparison")
    
    # Connect comparison -> check_faq
    workflow.add_edge("comparison", "check_faq")
    
    # Connect faq -> END
    workflow.add_edge("faq", END)
    
    # Compile and return
    app = workflow.compile()
    logger.info("LangGraph workflow compiled successfully")
    
    return app


def run_workflow(product_data, operations: List[str]) -> dict:
    """Run the LangGraph workflow.
    
    Args:
        product_data: Input product data (dict or string)
        operations: List of operations to perform ['description', 'comparison', 'faq']
        
    Returns:
        Results dictionary with requested outputs
    """
    logger.info(f"Running workflow with operations: {operations}")
    
    # Create initial state
    initial_state: AgentState = {
        'input_data': product_data,
        'operations': operations,
        'parsed_data': None,
        'description': None,
        'similar_products': None,
        'comparison': None,
        'faqs': None,
        'error': None
    }
    
    # Get compiled workflow
    app = create_workflow()
    
    # Run workflow
    final_state = app.invoke(initial_state)
    
    # Build results
    results = {
        'product_data': final_state.get('parsed_data')
    }
    
    if 'description' in operations and final_state.get('description'):
        results['description'] = final_state['description']
    
    if 'comparison' in operations and final_state.get('comparison'):
        results['comparison'] = final_state['comparison']
    
    if 'faq' in operations and final_state.get('faqs'):
        results['faqs'] = final_state['faqs']
    
    if final_state.get('error'):
        results['error'] = final_state['error']
    
    logger.info("Workflow execution completed")
    
    return results
