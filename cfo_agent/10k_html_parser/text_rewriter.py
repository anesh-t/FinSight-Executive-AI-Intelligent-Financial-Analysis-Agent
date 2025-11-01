"""
Text Rewriter - Uses LLM to fix parsing errors and clean text
"""
import time
from typing import Optional
from openai import OpenAI

class TextRewriter:
    """Uses free-tier LLM to fix and clean parsed text"""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.get_openai_key())
        self.cache = {}
        
    def rewrite_if_needed(self, text: str, context: str = "") -> str:
        """
        Check if text needs rewriting and fix if necessary
        
        Args:
            text: Original text
            context: Context (section name, etc.)
            
        Returns:
            Cleaned/rewritten text
        """
        if not self.config.ENABLE_TEXT_REWRITING:
            return text
        
        if not self._has_parsing_errors(text):
            return text
        
        print(f"   🔧 Rewriting text with parsing errors...")
        
        rewritten = self._rewrite_with_llm(text, context)
        
        return rewritten if rewritten else text
    
    def _has_parsing_errors(self, text: str) -> bool:
        """Detect if text has parsing errors"""
        
        indicators = [
            len([c for c in text if c.isupper()]) / len(text) > 0.5 if text else False,
            '...' in text and text.count('...') > 3,
            len(text.split()) < 10 and len(text) > 100,
            text.count('\n\n\n') > 2,
            text.count('  ') > 10,
        ]
        
        return any(indicators)
    
    def _rewrite_with_llm(self, text: str, context: str) -> Optional[str]:
        """Use LLM to rewrite/fix text"""
        
        cache_key = hash(text[:200])
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        prompt = f"""Fix text from HTML parsing. Remove artifacts, fix formatting.

Context: {context}

Text: {text}

Output clean, readable text preserving all information."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Fix parsing errors. Keep all data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=1000
            )
            
            rewritten = response.choices[0].message.content.strip()
            self.cache[cache_key] = rewritten
            return rewritten
            
        except Exception as e:
            print(f"   ⚠️  LLM rewrite failed: {e}")
            return None
    
    def generate_subheading(self, text: str, context: str = "") -> Optional[str]:
        """Generate a descriptive subheading for text"""
        
        if not self.config.ENABLE_AI_SUBHEADINGS:
            return None
        
        text_sample = text[:500]
        
        prompt = f"""Generate a 3-8 word subheading for this text.

Context: {context}
Text: {text_sample}

Output only the subheading."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Generate concise subheadings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=50
            )
            
            subheading = response.choices[0].message.content.strip()
            subheading = subheading.strip('"\'')
            
            return subheading
            
        except Exception as e:
            print(f"   ⚠️  Subheading generation failed: {e}")
            return None
