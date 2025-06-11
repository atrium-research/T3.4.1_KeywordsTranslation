from groq import Groq
from openai import OpenAI, api_key
from anthropic import Anthropic
from tenacity import retry, wait_random_exponential, stop_after_attempt
from abc import ABC, abstractmethod

# Abstract base class for LLM clients
class LLMClient(ABC):
    """Abstract base class for LLM clients to ensure consistent interface."""
    
    @abstractmethod
    def generate_response(self, system_message: str, user_message: str) -> str:
        """Generate a response using the LLM."""
        pass

# OpenAI client wrapper
class OpenAIClient(LLMClient):
    """Wrapper for OpenAI client."""
    
    def __init__(self, api_key, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_response(self, system_message: str, user_message: str) -> str:
        """Generate response using OpenAI API with retry logic."""
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=self.model_name
        )
        return completion.choices[0].message.content
    
# OpenAI client wrapper
class OpenAIWebSearchClient(LLMClient):
    """Wrapper for OpenAI client."""
    
    def __init__(self, api_key, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_response(self, system_message: str, user_message: str) -> str:
        """Generate response using OpenAI API with retry logic."""
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=self.model_name,
            web_search_options={}
        )
        return completion.choices[0].message.content
    
class GroqClient(LLMClient):
    """Wrapper for OpenAI client."""
    
    def __init__(self, api_key, model_name: str):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_response(self, system_message: str, user_message: str) -> str:
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=self.model_name
        )
        return completion.choices[0].message.content

# Anthropic client wrapper example
class AnthropicClient(LLMClient):
    """Wrapper for Anthropic client."""
    
    def __init__(self, api_key, model_name: str):
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_response(self, system_message: str, user_message: str) -> str:
        """Generate response using Anthropic API with retry logic."""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=4000,
            system=system_message,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    