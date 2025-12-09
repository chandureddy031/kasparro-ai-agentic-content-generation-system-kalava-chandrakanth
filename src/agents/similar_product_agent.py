import json
from llm_client import LLMClient


class SimilarProductAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "Similar Product Agent"

    # -------------------------------
    # Utility: Clean JSON returned by LLM
    # -------------------------------
    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1]
        return text.strip()

    # -------------------------------
    # Step 1: Find Similar Products
    # -------------------------------
    def find_similar_products(self, product_data: dict):
        product_name = product_data.get("product_name", "Unknown Product")
        ingredients = product_data.get("key_ingredients", "")
        price = product_data.get("price_in_inr", "")

        prompt = f"""
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

JSON FORMAT:
[
  {{
    "brand": "Brand",
    "product_name": "Product Name",
    "key_features": "Key features",
    "price": "Rs 699",
    "rating": 4.3,
    "rating_source": "estimated",
    "differentiators": "What makes it different"
  }}
]
"""

        response = self.llm_client.generate(prompt, temperature=0.6)

        try:
            cleaned = self._clean_json(response)
            data = json.loads(cleaned)

            if isinstance(data, list) and len(data) == 3:
                return data
        except Exception:
            pass

        return self._generate_fallback_products(product_name, price)

    # -------------------------------
    # Fallback Products (Deterministic)
    # -------------------------------
    def _generate_fallback_products(self, product_name, price):
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

    # -------------------------------
    # Step 2: Compare Products
    # -------------------------------
    def compare_products(self, original_product, similar_products, template):
        if not similar_products:
            similar_products = self._generate_fallback_products(
                original_product.get("product_name", ""),
                original_product.get("price_in_inr", "")
            )

        prompt = f"""
Compare the ORIGINAL product with the ALTERNATIVE products.

ORIGINAL PRODUCT:
{json.dumps(original_product, indent=2)}

ALTERNATIVE PRODUCTS:
{json.dumps(similar_products, indent=2)}

MANDATORY OUTPUT KEYS (JSON ONLY):
comparison_basis
comparison_summary
feature_comparison
price_analysis
recommendations
best_value_pick

IMPORTANT:
- Ratings are ESTIMATED
- Do NOT invent external data
- No markdown
"""

        response = self.llm_client.generate(prompt, temperature=0.7)

        try:
            cleaned = self._clean_json(response)
            analysis = json.loads(cleaned)
        except Exception:
            analysis = {
                "comparison_summary": "Comparison completed using fallback logic",
                "feature_comparison": [],
                "price_analysis": {},
                "recommendations": {},
                "best_value_pick": {}
            }

        # ✅ FINAL CLEAN STRUCTURE (NO DOUBLE NESTING)
        return {
            "product_data": original_product,
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
