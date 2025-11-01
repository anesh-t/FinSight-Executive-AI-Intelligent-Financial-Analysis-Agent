"""
Response Generator - Generate CFO-level answers from retrieved context
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config

# Import from same directory
from llm_client import LLMClient, LLMResponse
from cfo_prompts import (
    CFO_SYSTEM_MESSAGE,
    RISK_ANALYSIS_PROMPT,
    COMPARISON_PROMPT,
    STRATEGIC_EXPLANATION_PROMPT,
    TREND_ANALYSIS_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    METRICS_EXPLANATION_PROMPT,
    select_prompt
)

# Import from retrieval module
sys.path.insert(0, str(Path(__file__).parent.parent / '2_retrieval'))
from context_builder import ContextWindow


@dataclass
class GeneratedAnswer:
    """Generated answer with metadata"""
    text: str
    query: str
    prompt_type: str
    llm_response: LLMResponse
    citations: Dict[int, str]
    
    def __str__(self):
        return f"GeneratedAnswer(tokens={self.llm_response.total_tokens}, cost=${self.llm_response.cost:.4f})"


class ResponseGenerator:
    """Generate CFO-level answers using GPT-4"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize response generator.
        
        Args:
            model: LLM model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens for answer
        """
        self.llm_client = LLMClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        print("✅ Response Generator initialized")
    
    def generate(
        self,
        query: str,
        context: ContextWindow,
        prompt_type: str = None
    ) -> GeneratedAnswer:
        """
        Generate answer from query and context.
        
        Args:
            query: User query
            context: Retrieved context
            prompt_type: Explicit prompt type (auto-detected if None)
            
        Returns:
            GeneratedAnswer with text and metadata
        """
        # Select appropriate prompt
        prompt_template = select_prompt(query, prompt_type)
        
        # Format prompt with context
        formatted_prompt = prompt_template.format(
            context=context.formatted_context,
            query=query
        )
        
        # Generate response
        print(f"🤖 Generating CFO-level analysis...")
        llm_response = self.llm_client.generate(
            prompt=formatted_prompt,
            system_message=CFO_SYSTEM_MESSAGE
        )
        
        print(f"✅ Answer generated: {llm_response.total_tokens} tokens, ${llm_response.cost:.4f}")
        
        return GeneratedAnswer(
            text=llm_response.text,
            query=query,
            prompt_type=prompt_type or "auto",
            llm_response=llm_response,
            citations=context.citations
        )
    
    def generate_with_type(
        self,
        query: str,
        context: ContextWindow,
        answer_type: str
    ) -> GeneratedAnswer:
        """
        Generate answer with explicit type.
        
        Args:
            query: User query
            context: Retrieved context
            answer_type: 'risk', 'comparison', 'strategy', 'trend', 'summary', 'metrics'
            
        Returns:
            GeneratedAnswer
        """
        return self.generate(query, context, prompt_type=answer_type)


if __name__ == "__main__":
    print("Response Generator module - Use via RAG Agent")
