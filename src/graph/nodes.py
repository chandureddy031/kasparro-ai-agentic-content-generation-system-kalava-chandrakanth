"""LangGraph node functions for the workflow.

These functions transform the AgentState and are used as nodes in the LangGraph workflow.
"""
import json
import logging
from typing import Dict, Any

from models.state import AgentState
from models.outputs import ParsedProduct, ProductDescription, FAQPage, ProductComparison
from llm_client import LLMClient

logger = logging.getLogger(__name__)


def parser_node(state: AgentState) -> AgentState:
    """Parse product data and extract structured information.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with parsed_data
    """
    logger.info("Parser node executing...")
    
    llm_client = LLMClient()
    product_data = state.get('input_data')
    
    # If already a dict, validate and use it
    if isinstance(product_data, dict):
        try:
            parsed = ParsedProduct.model_validate(product_data)
            state['parsed_data'] = parsed.model_dump()
            return state
        except Exception as e:
            logger.warning(f"Dict validation failed, will parse: {e}")
    
    # Parse text input
    prompt = f"""Extract product information from text and return as JSON:

{product_data}

Return JSON with fields: product_name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price

Ensure all string fields are present (use empty string if not found)."""
    
    try:
        parsed = llm_client.generate_structured(prompt, ParsedProduct)
        state['parsed_data'] = parsed.model_dump()
        logger.info(f"Parsed product: {parsed.product_name}")
    except Exception as e:
        logger.error(f"Parser failed: {e}")
        state['parsed_data'] = {"product_name": "Unknown", "raw_data": str(product_data)}
        state['error'] = f"Parser error: {str(e)}"
    
    return state


def description_node(state: AgentState) -> AgentState:
    """Generate product description.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with description
    """
    logger.info("Description node executing...")
    
    llm_client = LLMClient()
    parsed_data = state.get('parsed_data', {})
    
    # Load template
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(current_dir, 'templates', 'product_description.txt')
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
    except Exception as e:
        logger.warning(f"Could not load template: {e}")
        template = "Create a professional product description."
    
    prompt = f"""Using template and product data, create product description:

TEMPLATE:
{template}

PRODUCT:
{json.dumps(parsed_data, indent=2)}

Return JSON with: title, description, highlights (array), usage_instructions"""
    
    try:
        description = llm_client.generate_structured(prompt, ProductDescription)
        state['description'] = description.model_dump()
        logger.info("Description generated successfully")
    except Exception as e:
        logger.error(f"Description generation failed: {e}")
        state['description'] = {
            "title": parsed_data.get('product_name', 'Product'),
            "description": "Description generation failed",
            "highlights": [],
            "usage_instructions": ""
        }
        state['error'] = f"Description error: {str(e)}"
    
    return state


def faq_node(state: AgentState) -> AgentState:
    """Generate FAQs (minimum 15).
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with faqs
    """
    logger.info("FAQ node executing...")
    
    llm_client = LLMClient()
    parsed_data = state.get('parsed_data', {})
    
    # Load template
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(current_dir, 'templates', 'faq_template.txt')
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
    except Exception as e:
        logger.warning(f"Could not load template: {e}")
        template = "Generate comprehensive FAQs with categories."
    
    prompt = f"""Create MINIMUM 15 FAQs for this product with categories:

PRODUCT:
{json.dumps(parsed_data, indent=2)}

TEMPLATE:
{template}

Return JSON with array of FAQs. Each FAQ must have:
- question: string
- answer: string (3-5 sentences)
- category: one of [Informational, Safety, Usage, Purchase, Comparison]

MINIMUM 15 FAQs REQUIRED."""
    
    try:
        faq_page = llm_client.generate_structured(prompt, FAQPage, max_tokens=4096)
        state['faqs'] = [faq.model_dump() for faq in faq_page.faqs]
        logger.info(f"Generated {len(faq_page.faqs)} FAQs")
    except Exception as e:
        logger.error(f"FAQ generation failed: {e}")
        # Fallback: generate minimum FAQs manually
        state['faqs'] = _generate_fallback_faqs(parsed_data)
        state['error'] = f"FAQ error: {str(e)}"
    
    return state


def comparison_node(state: AgentState) -> AgentState:
    """Find similar products and compare.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with comparison data
    """
    logger.info("Comparison node executing...")
    
    llm_client = LLMClient()
    parsed_data = state.get('parsed_data', {})
    
    # Step 1: Find similar products
    product_name = parsed_data.get("product_name", "Unknown Product")
    ingredients = parsed_data.get("key_ingredients", "")
    price = parsed_data.get("price", "")
    
    similar_prompt = f"""
You are a skincare market research expert.

ORIGINAL PRODUCT
Name: {product_name}
Ingredients: {ingredients}
Price: {price}

TASK
Return EXACTLY 3 real competing products from the Indian market (2025).

RULES
- Different brands
- JSON ONLY
- No markdown
- Ratings must be ESTIMATED

JSON FORMAT (return array of 3 objects):
[
  {{
    "brand": "Brand Name",
    "product_name": "Product Name",
    "key_features": "Key features description",
    "price": "Rs 699",
    "rating": 4.3,
    "rating_source": "estimated",
    "differentiators": "What makes it different"
  }}
]
"""
    
    try:
        # Get similar products as raw JSON first
        response = llm_client.generate(similar_prompt, temperature=0.6)
        cleaned = llm_client._clean_json(response)
        similar_products = json.loads(cleaned)
        
        if not isinstance(similar_products, list) or len(similar_products) != 3:
            raise ValueError("Expected exactly 3 products")
        
        state['similar_products'] = similar_products
        logger.info(f"Found {len(similar_products)} similar products")
    except Exception as e:
        logger.warning(f"Similar product search failed, using fallback: {e}")
        similar_products = _generate_fallback_products(product_name, price)
        state['similar_products'] = similar_products
    
    # Step 2: Compare products
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(current_dir, 'templates', 'comparison_template.txt')
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
    except Exception:
        template = "Compare products based on features and price."
    
    comparison_prompt = f"""
Compare the ORIGINAL product with the ALTERNATIVE products.

ORIGINAL PRODUCT:
{json.dumps(parsed_data, indent=2)}

ALTERNATIVE PRODUCTS:
{json.dumps(similar_products, indent=2)}

TEMPLATE:
{template}

Return JSON with:
- comparison_summary: string
- feature_comparison: array of comparison points
- price_analysis: object with price insights
- recommendations: object with recommendation
- best_value_pick: object with best value selection

IMPORTANT:
- Ratings are ESTIMATED
- Do NOT invent external data
- No markdown
"""
    
    try:
        # Get comparison as raw JSON
        response = llm_client.generate(comparison_prompt, temperature=0.7, max_tokens=2048)
        cleaned = llm_client._clean_json(response)
        analysis = json.loads(cleaned)
        
        comparison = {
            "product_data": parsed_data,
            "comparison_basis": {
                "primary_factors": [
                    "Active ingredient type",
                    "Ingredient concentration",
                    "Skin type suitability",
                    "Price"
                ],
                "assumptions": [
                    "Ratings are estimated",
                    "Brand reputation inferred"
                ]
            },
            "similar_products": similar_products,
            "analysis": analysis
        }
        
        state['comparison'] = comparison
        logger.info("Comparison completed successfully")
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        state['comparison'] = {
            "product_data": parsed_data,
            "similar_products": similar_products,
            "analysis": {
                "comparison_summary": "Comparison failed",
                "feature_comparison": [],
                "price_analysis": {},
                "recommendations": {},
                "best_value_pick": {}
            }
        }
        state['error'] = f"Comparison error: {str(e)}"
    
    return state


def _generate_fallback_faqs(product_data: Dict[str, Any]) -> list:
    """Generate fallback FAQs if LLM fails.
    
    Args:
        product_data: Parsed product information
        
    Returns:
        List of 15 basic FAQs
    """
    product_name = product_data.get('product_name', 'this product')
    
    faqs = [
        # Informational (3)
        {
            "question": f"What is {product_name}?",
            "answer": f"{product_name} is a skincare product designed to address specific skin concerns. It contains carefully selected ingredients to deliver effective results.",
            "category": "Informational"
        },
        {
            "question": f"Who should use {product_name}?",
            "answer": f"{product_name} is suitable for individuals looking to improve their skin health. Consult with a dermatologist to ensure it matches your skin type and concerns.",
            "category": "Informational"
        },
        {
            "question": f"What makes {product_name} unique?",
            "answer": f"{product_name} stands out due to its formulation and ingredient selection. It's designed to provide targeted benefits for your skincare routine.",
            "category": "Informational"
        },
        # Safety (3)
        {
            "question": f"Is {product_name} safe for sensitive skin?",
            "answer": "Always perform a patch test before using any new skincare product. If you have sensitive skin, consult a dermatologist before use.",
            "category": "Safety"
        },
        {
            "question": f"Are there any side effects of using {product_name}?",
            "answer": "Side effects vary by individual. Common reactions may include mild irritation or redness. Discontinue use if severe reactions occur and consult a healthcare professional.",
            "category": "Safety"
        },
        {
            "question": "What ingredients should I be cautious about?",
            "answer": "Check the ingredient list for any known allergens or irritants specific to your skin. If you have allergies, consult with a dermatologist before use.",
            "category": "Safety"
        },
        # Usage (3)
        {
            "question": f"How do I use {product_name}?",
            "answer": "Follow the instructions on the product packaging. Typically, skincare products are applied to clean, dry skin in the recommended amounts.",
            "category": "Usage"
        },
        {
            "question": f"When should I apply {product_name}?",
            "answer": "Application timing depends on the product type. Serums are often applied in the morning or evening, while some products are designed for specific times of day.",
            "category": "Usage"
        },
        {
            "question": "How much product should I use per application?",
            "answer": "Use as directed on the packaging. Typically, a few drops or a pea-sized amount is sufficient for most skincare products to avoid waste and ensure effectiveness.",
            "category": "Usage"
        },
        # Purchase (3)
        {
            "question": f"What is the price of {product_name}?",
            "answer": f"The price is {product_data.get('price', 'available on the product listing')}. Prices may vary by retailer and location.",
            "category": "Purchase"
        },
        {
            "question": f"Is {product_name} worth the investment?",
            "answer": "Value depends on your skincare goals and budget. Consider the ingredient quality, brand reputation, and your specific needs when evaluating worth.",
            "category": "Purchase"
        },
        {
            "question": f"Where can I buy {product_name}?",
            "answer": f"{product_name} is typically available through authorized retailers, online marketplaces, and official brand websites. Ensure you purchase from trusted sources.",
            "category": "Purchase"
        },
        # Comparison (3)
        {
            "question": f"How does {product_name} compare to similar products?",
            "answer": f"{product_name} has its own unique formulation and benefits. Compare ingredient lists, concentrations, and reviews to find the best match for your needs.",
            "category": "Comparison"
        },
        {
            "question": "What are some alternatives to this product?",
            "answer": "There are various alternatives in the market with similar active ingredients. Research and compare products based on your specific skin concerns and budget.",
            "category": "Comparison"
        },
        {
            "question": f"Why should I choose {product_name} over other options?",
            "answer": f"Choose {product_name} based on its specific formulation, ingredient quality, and how well it addresses your skincare needs compared to alternatives.",
            "category": "Comparison"
        },
    ]
    
    return faqs


def _generate_fallback_products(product_name: str, price: str) -> list:
    """Generate fallback similar products.
    
    Args:
        product_name: Original product name
        price: Original product price
        
    Returns:
        List of 3 similar products
    """
    try:
        price_value = int("".join(c for c in str(price) if c.isdigit()))
        if price_value <= 0:
            price_value = 800
    except Exception:
        price_value = 800
    
    return [
        {
            "brand": "Minimalist",
            "product_name": "Hyaluronic Acid 2% + B5 Serum",
            "key_features": "2% Hyaluronic Acid, Vitamin B5",
            "price": f"Rs {price_value - 50}",
            "rating": 4.4,
            "rating_source": "estimated",
            "differentiators": "Fragrance-free, simple formulation"
        },
        {
            "brand": "Mamaearth",
            "product_name": "Hyaluronic Acid Serum",
            "key_features": "Hyaluronic Acid, Vitamin B5",
            "price": f"Rs {price_value}",
            "rating": 4.3,
            "rating_source": "estimated",
            "differentiators": "Toxin-free, cruelty-free"
        },
        {
            "brand": "Lakme",
            "product_name": "9 to 5 Hyaluronic Acid Serum",
            "key_features": "Hyaluronic Acid, Vitamin E",
            "price": f"Rs {price_value + 150}",
            "rating": 4.2,
            "rating_source": "estimated",
            "differentiators": "Lightweight daily-use serum"
        }
    ]
