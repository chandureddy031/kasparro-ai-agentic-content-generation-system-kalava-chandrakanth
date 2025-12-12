"""Integration test for workflow structure (no API calls)."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.state import AgentState
from graph.workflow import create_workflow


def test_workflow_structure():
    """Test that the workflow can be created and compiled."""
    try:
        app = create_workflow()
        print("✓ Test passed: Workflow compiled successfully")
        
        # Check that the workflow has nodes
        assert app is not None
        print("✓ Test passed: Workflow is not None")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_conditional_routing():
    """Test that conditional routing functions work correctly."""
    from graph.workflow import route_after_parser, route_after_description, route_after_comparison
    
    # Test parser routing
    state: AgentState = {
        'operations': ['description', 'faq'],
        'input_data': {},
        'parsed_data': None,
        'faqs': None,
        'error': None
    }
    
    next_node = route_after_parser(state)
    assert next_node == 'description', f"Expected 'description', got '{next_node}'"
    print("✓ Test passed: Parser routes to description correctly")
    
    # Test description routing to FAQ
    next_node = route_after_description(state)
    assert next_node == 'faq', f"Expected 'faq', got '{next_node}'"
    print("✓ Test passed: Description routes to FAQ correctly")
    
    # Test comparison routing when FAQ is requested
    state['operations'] = ['comparison', 'faq']
    next_node = route_after_comparison(state)
    assert next_node == 'faq', f"Expected 'faq', got '{next_node}'"
    print("✓ Test passed: Comparison routes to FAQ correctly")
    
    # Test routing to END when no more operations
    state['operations'] = ['description']
    next_node = route_after_description(state)
    assert next_node == '__end__', f"Expected '__end__', got '{next_node}'"
    print("✓ Test passed: Routes to END correctly")
    
    return True


if __name__ == "__main__":
    print("\nRunning workflow integration tests...\n")
    
    success = True
    success = test_workflow_structure() and success
    success = test_workflow_conditional_routing() and success
    
    if success:
        print("\n✅ All workflow tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
