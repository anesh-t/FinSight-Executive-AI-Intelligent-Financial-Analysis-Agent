"""
Answer Formatter - Format and post-process generated answers
"""

from typing import Dict, List
from dataclasses import dataclass
import re

from response_generator import GeneratedAnswer


@dataclass
class FormattedAnswer:
    """Formatted answer ready for display"""
    text: str
    query: str
    sources: str
    metadata: Dict
    
    def display(self):
        """Display formatted answer"""
        print("=" * 80)
        print(self.text)
        print()
        print("─" * 80)
        print(self.sources)
        print()
        print(f"⏱️  Query time: {self.metadata['latency']:.1f}s | "
              f"💰 Cost: ${self.metadata['cost']:.4f} | "
              f"📊 Tokens: {self.metadata['tokens']}")
        print("=" * 80)
    
    def to_markdown(self) -> str:
        """Export as markdown"""
        return f"""{self.text}

---

{self.sources}

*Analysis completed in {self.metadata['latency']:.1f}s | Cost: ${self.metadata['cost']:.4f}*
"""


class AnswerFormatter:
    """Format generated answers for display"""
    
    def format(self, answer: GeneratedAnswer) -> FormattedAnswer:
        """
        Format generated answer.
        
        Args:
            answer: Generated answer
            
        Returns:
            FormattedAnswer ready for display
        """
        # Clean up answer text
        text = self._clean_text(answer.text)
        
        # Format sources
        sources = self._format_sources(answer.citations)
        
        # Build metadata
        metadata = {
            'query': answer.query,
            'prompt_type': answer.prompt_type,
            'tokens': answer.llm_response.total_tokens,
            'cost': answer.llm_response.cost,
            'latency': answer.llm_response.latency,
            'model': answer.llm_response.model,
            'source_count': len(answer.citations)
        }
        
        return FormattedAnswer(
            text=text,
            query=answer.query,
            sources=sources,
            metadata=metadata
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean up answer text"""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Ensure proper spacing around headers
        text = re.sub(r'([^\n])\n(═+)', r'\1\n\n\2', text)
        text = re.sub(r'(═+)\n([^\n])', r'\1\n\n\2', text)
        
        return text.strip()
    
    def _format_sources(self, citations: Dict[int, str]) -> str:
        """Format citation sources"""
        if not citations:
            return "📚 SOURCES\nNo specific sources cited."
        
        lines = ["📚 SOURCES"]
        for num in sorted(citations.keys()):
            lines.append(f"[{num}] {citations[num]}")
        
        return "\n".join(lines)
    
    def format_simple(self, answer: GeneratedAnswer) -> str:
        """Simple text format (just answer + sources)"""
        return f"{answer.text}\n\n{self._format_sources(answer.citations)}"
    
    def format_json(self, answer: GeneratedAnswer) -> Dict:
        """Format as JSON structure"""
        return {
            'query': answer.query,
            'answer': answer.text,
            'sources': [
                {'number': num, 'citation': cite}
                for num, cite in sorted(answer.citations.items())
            ],
            'metadata': {
                'prompt_type': answer.prompt_type,
                'model': answer.llm_response.model,
                'tokens': answer.llm_response.total_tokens,
                'cost': answer.llm_response.cost,
                'latency': answer.llm_response.latency
            }
        }


if __name__ == "__main__":
    print("Answer Formatter module - Use via RAG Agent")
