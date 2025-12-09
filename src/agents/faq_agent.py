import json
from llm_client import LLMClient

class FAQAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = "FAQ Agent"
    
    def generate_faqs(self, product_data, template, num_faqs=10):
        prompt = f"""Create {num_faqs} FAQs for this product:

PRODUCT:
{json.dumps(product_data, indent=2)}

TEMPLATE:
{template}

Return JSON array with: question, answer"""
        
        response = self.llm_client.generate_json(prompt)
        
        try:
            faqs = json.loads(response)
            return faqs
        except:
            return [{"question": "FAQ Generation", "answer": response}]
