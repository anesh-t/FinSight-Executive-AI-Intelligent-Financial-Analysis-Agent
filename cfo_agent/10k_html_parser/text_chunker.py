"""
Text Chunker - Splits long text into chunks with AI-generated subheadings
"""
import re
from typing import List, Dict, Any
from openai import OpenAI

class TextChunker:
    """Chunks long text and generates subheadings"""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.get_openai_key())
        
    def chunk_if_needed(self, text: str, context: str = "") -> List[Dict[str, Any]]:
        """
        Chunk text if it exceeds threshold
        
        Args:
            text: Text to chunk
            context: Section context
            
        Returns:
            List of chunks with subheadings
        """
        word_count = len(text.split())
        
        if word_count <= self.config.MAX_CHUNK_WORDS:
            return [{
                "text": text,
                "word_count": word_count,
                "subheading": None
            }]
        
        print(f"   ✂️  Chunking long text ({word_count} words)...")
        
        chunks = self._split_text_smartly(text)
        
        chunks_with_headings = []
        for i, chunk in enumerate(chunks):
            subheading = self._generate_chunk_subheading(chunk, context, i+1, len(chunks))
            chunks_with_headings.append({
                "text": chunk,
                "word_count": len(chunk.split()),
                "subheading": subheading,
                "chunk_index": i + 1,
                "total_chunks": len(chunks)
            })
        
        return chunks_with_headings
    
    def _split_text_smartly(self, text: str) -> List[str]:
        """Split text at natural boundaries"""
        
        # First try paragraph splits
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            para_words = len(para.split())
            
            # If a single paragraph is too long, split by sentences
            if para_words > self.config.OPTIMAL_CHUNK_SIZE:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                # Split long paragraph by sentences
                sentences = para.split('. ')
                sent_chunk = []
                sent_count = 0
                
                for sent in sentences:
                    sent_words = len(sent.split())
                    if sent_count + sent_words <= self.config.OPTIMAL_CHUNK_SIZE:
                        sent_chunk.append(sent)
                        sent_count += sent_words
                    else:
                        if sent_chunk:
                            chunks.append('. '.join(sent_chunk) + '.')
                        sent_chunk = [sent]
                        sent_count = sent_words
                
                if sent_chunk:
                    chunks.append('. '.join(sent_chunk) + '.')
                
                continue
            
            if current_word_count + para_words <= self.config.OPTIMAL_CHUNK_SIZE:
                current_chunk.append(para)
                current_word_count += para_words
            else:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_word_count = para_words
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _generate_chunk_subheading(self, chunk: str, context: str, index: int, total: int) -> str:
        """Generate subheading for chunk using LLM"""
        
        text_sample = chunk[:400]
        
        prompt = f"""Generate a descriptive 4-8 word subheading for this text chunk.

Context: {context}
Chunk {index} of {total}

Text: {text_sample}

Output only the subheading, no quotes."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Generate concise, descriptive subheadings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=50
            )
            
            subheading = response.choices[0].message.content.strip()
            subheading = subheading.strip('"\'')
            
            if not subheading:
                subheading = f"Section {index} of {total}"
            
            return subheading
            
        except Exception as e:
            print(f"   ⚠️  Subheading generation failed: {e}")
            return f"Part {index}"
