import json
from llm_client import LLMClient

class ParserAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "Parser Agent"
    
    def parse_product(self, product_data):
        if isinstance(product_data, dict):
            return product_data
        
        prompt = f"""Extract product information from text and return as JSON:

{product_data}

Return JSON with fields: product_name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price"""
        
        response = self.llm_client.generate_json(prompt)
        
        try:
            parsed_data = json.loads(response)
            return parsed_data
        except:
            return {"raw_data": product_data}
    
    def generate_description(self, product_data, template):
        prompt = f"""Using template and product data, create product description:

TEMPLATE:
{template}

PRODUCT:
{json.dumps(product_data, indent=2)}

Return JSON with: title, description, highlights, usage_instructions"""
        
        response = self.llm_client.generate_json(prompt)
        
        try:
            description = json.loads(response)
            return description
        except:
            return {"description": response}
