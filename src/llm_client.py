from groq import Groq
from config import Config

class LLMClient:
    def __init__(self):
        Config.validate()
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.MODEL_NAME
    
    def generate(self, prompt, temperature=None, max_tokens=None):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or Config.TEMPERATURE,
                max_tokens=max_tokens or Config.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_json(self, prompt):
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON format."
        return self.generate(json_prompt)
