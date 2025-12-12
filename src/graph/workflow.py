"""LangGraph workflow definition.

This module defines the StateGraph that orchestrates all agents using LangGraph.
"""
import logging
from typing import List, Literal
from langgraph.graph import StateGraph, END

from models.state import AgentState
from graph.nodes import parser_node, description_node, faq_node, comparison_node

logger = logging.getLogger(__name__)


def route_after_parser(state: AgentState) -> Literal["description", "comparison", "faq", "__end__"]:
    """Route from parser to the first requested operation.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    operations = state.get('operations', [])
    if 'description' in operations:
        return 'description'
    elif 'comparison' in operations:
        return 'comparison'
    elif 'faq' in operations:
        return 'faq'
    return END


def route_after_description(state: AgentState) -> Literal["comparison", "faq", "__end__"]:
    """Route from description to next operation.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or END
    """
    operations = state.get('operations', [])
    if 'comparison' in operations:
        return 'comparison'
    elif 'faq' in operations:
        return 'faq'
    return END


def route_after_comparison(state: AgentState) -> Literal["faq", "__end__"]:
    """Route from comparison to FAQ or END.
    
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
        route_after_parser,
        {
            "description": "description",
            "comparison": "comparison",
            "faq": "faq",
            END: END
        }
    )
    
    # Add conditional edges from description
    workflow.add_conditional_edges(
        "description",
        route_after_description,
        {
            "comparison": "comparison",
            "faq": "faq",
            END: END
        }
    )
    
    # Add conditional edges from comparison
    workflow.add_conditional_edges(
        "comparison",
        route_after_comparison,
        {
            "faq": "faq",
            END: END
        }
    )
    
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
