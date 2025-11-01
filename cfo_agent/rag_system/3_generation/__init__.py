"""
Module 3: Response Generation
CFO-level answer generation with GPT-4
"""

from .llm_client import LLMClient, LLMResponse
from .response_generator import ResponseGenerator, GeneratedAnswer
from .answer_formatter import AnswerFormatter, FormattedAnswer
from .rag_agent import RAGAgent

__all__ = [
    'LLMClient',
    'LLMResponse',
    'ResponseGenerator',
    'GeneratedAnswer',
    'AnswerFormatter',
    'FormattedAnswer',
    'RAGAgent'
]
