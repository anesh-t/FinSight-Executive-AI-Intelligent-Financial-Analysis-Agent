"""
LLM Client - OpenAI GPT-4 Integration
Handles API calls, token counting, and cost tracking
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time
from openai import OpenAI
import tiktoken

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config


@dataclass
class LLMResponse:
    """LLM response with metadata"""
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency: float  # seconds
    
    def __str__(self):
        return f"LLMResponse(tokens={self.total_tokens}, cost=${self.cost:.4f}, time={self.latency:.1f}s)"


class LLMClient:
    """OpenAI GPT-4 client with cost tracking"""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    }
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize LLM client.
        
        Args:
            model: Model name (defaults to config)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum completion tokens
        """
        self.model = model or config.llm.get_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client
        api_key = config.llm.get_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        self.client = OpenAI(api_key=api_key)
        
        # Token counter
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to cl100k_base for newer models
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        print(f"✅ LLM Client initialized: {self.model}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate API call cost"""
        pricing = self.PRICING.get(self.model, self.PRICING['gpt-4'])
        
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate completion from prompt.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            LLMResponse with text and metadata
        """
        start_time = time.time()
        
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            # Extract response
            text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # Calculate cost and latency
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            latency = time.time() - start_time
            
            return LLMResponse(
                text=text,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                latency=latency
            )
            
        except Exception as e:
            print(f"❌ LLM API Error: {e}")
            raise
    
    def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Generate completion with streaming (for real-time display).
        
        Yields text chunks as they arrive.
        """
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Streaming API call
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"❌ LLM Streaming Error: {e}")
            raise


def test_llm_client():
    """Test LLM client"""
    print("Testing LLM Client\n")
    
    client = LLMClient(model="gpt-4", temperature=0.1)
    
    # Test prompt
    prompt = """Based on this context from a 10-K filing:

"The Company faces cybersecurity threats that could materially impact operations and customer trust."

Question: What is the main risk?

Answer briefly:"""
    
    print("Sending test query...")
    response = client.generate(prompt)
    
    print(f"\n✅ Response: {response.text}")
    print(f"\n📊 Metadata:")
    print(f"   Model: {response.model}")
    print(f"   Tokens: {response.total_tokens} ({response.prompt_tokens} + {response.completion_tokens})")
    print(f"   Cost: ${response.cost:.4f}")
    print(f"   Time: {response.latency:.2f}s")
    print()


if __name__ == "__main__":
    test_llm_client()
