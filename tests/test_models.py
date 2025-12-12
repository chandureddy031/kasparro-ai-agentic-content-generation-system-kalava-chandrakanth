"""Unit tests for the multi-agent system."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.outputs import FAQ, FAQPage, ParsedProduct, ProductDescription
from models.state import AgentState


def test_faq_model_requires_minimum_15():
    """Test that FAQPage requires minimum 15 FAQs."""
    # Should fail with less than 15
    try:
        faqs_list = [
            FAQ(question=f"Q{i}", answer=f"A{i}", category="Informational")
            for i in range(10)
        ]
        faq_page = FAQPage(faqs=faqs_list)
        assert False, "Should have failed with less than 15 FAQs"
    except Exception as e:
        assert "at least 15 items" in str(e).lower() or "min_length" in str(e).lower()
        print("✓ Test passed: FAQPage rejects less than 15 FAQs")
    
    # Should succeed with 15 or more
    faqs_list = [
        FAQ(question=f"Q{i}", answer=f"A{i}", category="Informational")
        for i in range(15)
    ]
    faq_page = FAQPage(faqs=faqs_list)
    assert len(faq_page.faqs) == 15
    print("✓ Test passed: FAQPage accepts 15 FAQs")


def test_parsed_product_model():
    """Test ParsedProduct model validation."""
    product = ParsedProduct(
        product_name="Test Product",
        concentration="10%",
        skin_type="Oily",
        key_ingredients="Test Ingredient",
        benefits="Test Benefits",
        how_to_use="Apply daily",
        side_effects="None",
        price="₹699"
    )
    assert product.product_name == "Test Product"
    assert product.price == "₹699"
    print("✓ Test passed: ParsedProduct model validates correctly")


def test_faq_categories():
    """Test FAQ categories are properly defined."""
    categories = ["Informational", "Safety", "Usage", "Purchase", "Comparison"]
    
    for category in categories:
        faq = FAQ(
            question="Test question",
            answer="Test answer",
            category=category
        )
        assert faq.category == category
    
    print("✓ Test passed: FAQ categories work correctly")


def test_agent_state_structure():
    """Test AgentState TypedDict structure."""
    state: AgentState = {
        'input_data': {"product_name": "Test"},
        'operations': ['faq'],
        'parsed_data': None,
        'faqs': None,
        'error': None
    }
    
    assert 'input_data' in state
    assert 'operations' in state
    assert state['operations'] == ['faq']
    print("✓ Test passed: AgentState structure is correct")


if __name__ == "__main__":
    print("\nRunning unit tests...\n")
    
    test_parsed_product_model()
    test_faq_categories()
    test_faq_model_requires_minimum_15()
    test_agent_state_structure()
    
    print("\n✅ All tests passed!")
