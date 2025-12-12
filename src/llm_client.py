"""LLM client with structured output support and retry logic."""
import json
import logging
from typing import Type, TypeVar, Optional, Any
from groq import Groq
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class LLMClient:
    """LLM client with Pydantic model support and retry logic."""
    
    def __init__(self):
        Config.validate()
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.MODEL_NAME
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(
        self, 
        prompt: str, 
        temperature: Optional[float] = None, 
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text with retry logic.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (default from config)
            max_tokens: Maximum tokens to generate (default from config)
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all retry attempts fail
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or Config.TEMPERATURE,
                max_tokens=max_tokens or Config.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    def generate_json(self, prompt: str) -> str:
        """Generate JSON output (legacy method for compatibility).
        
        Args:
            prompt: Input prompt
            
        Returns:
            JSON string
        """
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON format."
        return self.generate(json_prompt)
    
    def generate_structured(
        self, 
        prompt: str, 
        model_class: Type[T],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> T:
        """Generate structured output using Pydantic model.
        
        Args:
            prompt: Input prompt
            model_class: Pydantic model class for output validation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If output cannot be parsed into model
        """
        # Add schema to prompt
        schema = model_class.model_json_schema()
        schema_prompt = f"""{prompt}

Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Do not include any markdown formatting or code blocks."""
        
        response = self.generate(schema_prompt, temperature, max_tokens)
        
        # Clean response
        cleaned = self._clean_json(response)
        
        try:
            # Parse and validate with Pydantic
            data = json.loads(cleaned)
            return model_class.model_validate(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}\nResponse: {response}")
            raise ValueError(f"Invalid JSON output: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to validate with Pydantic: {e}\nData: {cleaned}")
            raise ValueError(f"Invalid model structure: {str(e)}")
    
    @staticmethod
    def _clean_json(text: str) -> str:
        """Remove markdown formatting from JSON output.
        
        Args:
            text: Raw LLM output
            
        Returns:
            Cleaned JSON string
        """
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1]
        return text.strip()
