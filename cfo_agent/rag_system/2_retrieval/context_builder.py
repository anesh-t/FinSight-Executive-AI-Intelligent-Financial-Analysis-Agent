"""
Context Builder - Assembles retrieved chunks into LLM-ready context
Formats chunks with metadata and manages context length
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config
from semantic_retriever import RetrievedChunk
from table_extractor import TableExtractor


@dataclass
class ContextWindow:
    """Assembled context for LLM"""
    formatted_context: str  # Full formatted context
    chunks_used: List[RetrievedChunk]  # Chunks included
    total_tokens: int  # Estimated token count
    truncated: bool  # Whether context was truncated
    citations: Dict[int, str]  # Citation mapping


class ContextBuilder:
    """Builds formatted context from retrieved chunks"""
    
    def __init__(self, max_tokens: int = None):
        """
        Initialize context builder.
        
        Args:
            max_tokens: Maximum context length (from config if not specified)
        """
        self.max_tokens = max_tokens or config.llm.max_context_length
        # Reserve tokens for query and response
        self.chunk_token_limit = int(self.max_tokens * 0.6)  # 60% for chunks
        # Initialize table extractor
        self.table_extractor = TableExtractor()
    
    def build_context(
        self,
        chunks: List[RetrievedChunk],
        include_metadata: bool = True,
        include_citations: bool = True,
        format_style: str = "detailed"
    ) -> ContextWindow:
        """
        Build formatted context from chunks.
        
        Args:
            chunks: Retrieved chunks to include
            include_metadata: Include company/year/section metadata
            include_citations: Add citation numbers
            format_style: "detailed", "compact", or "minimal"
            
        Returns:
            ContextWindow with formatted context
        """
        if not chunks:
            return ContextWindow(
                formatted_context="No relevant information found.",
                chunks_used=[],
                total_tokens=0,
                truncated=False,
                citations={}
            )
        
        # Select format function
        if format_style == "detailed":
            format_func = self._format_detailed
        elif format_style == "compact":
            format_func = self._format_compact
        else:
            format_func = self._format_minimal
        
        # Build context with token limit
        context_parts = []
        chunks_used = []
        citations = {}
        total_tokens = 0
        truncated = False
        
        for i, chunk in enumerate(chunks, 1):
            # Format chunk
            formatted = format_func(chunk, citation_num=i if include_citations else None)
            chunk_tokens = self._estimate_tokens(formatted)
            
            # Check if adding this chunk exceeds limit
            if total_tokens + chunk_tokens > self.chunk_token_limit:
                truncated = True
                break
            
            context_parts.append(formatted)
            chunks_used.append(chunk)
            total_tokens += chunk_tokens
            
            if include_citations:
                citations[i] = self._create_citation(chunk)
        
        # Combine context
        separator = "\n\n" + "="*70 + "\n\n"
        formatted_context = separator.join(context_parts)
        
        return ContextWindow(
            formatted_context=formatted_context,
            chunks_used=chunks_used,
            total_tokens=total_tokens,
            truncated=truncated,
            citations=citations
        )
    
    def _format_detailed(self, chunk: RetrievedChunk, citation_num: Optional[int] = None) -> str:
        """Detailed format with full metadata and extracted tables"""
        parts = []
        
        # Citation header
        if citation_num:
            parts.append(f"[SOURCE {citation_num}]")
        
        # Metadata
        parts.append(
            f"Company: {chunk.company_name} ({chunk.ticker})\n"
            f"Year: {chunk.fiscal_year}\n"
            f"Section: {chunk.section} - {chunk.section_type}\n"
            f"Heading: {chunk.heading}"
        )
        
        if chunk.subheading:
            parts.append(f"Subheading: {chunk.subheading}")
        
        parts.append(f"Relevance: {chunk.similarity_score:.1%}")
        
        # Check for tables in content
        has_tables = self.table_extractor.detect_tables(chunk.chunk_text)
        
        if has_tables:
            # Extract and format tables
            tables = self.table_extractor.extract_tables(chunk.chunk_text)
            if tables:
                parts.append(f"\nContent (includes {len(tables)} table(s)):")
                parts.append(chunk.chunk_text)
                parts.append("\n📊 EXTRACTED TABLES:")
                for i, table in enumerate(tables, 1):
                    parts.append(f"\nTable {i}: {table.title}")
                    parts.append(table.to_formatted_text())
            else:
                parts.append(f"\nContent:\n{chunk.chunk_text}")
        else:
            parts.append(f"\nContent:\n{chunk.chunk_text}")
        
        return "\n".join(parts)
    
    def _format_compact(self, chunk: RetrievedChunk, citation_num: Optional[int] = None) -> str:
        """Compact format for efficiency with table extraction"""
        header = f"[{citation_num}] " if citation_num else ""
        header += f"{chunk.company_name} {chunk.fiscal_year} - {chunk.section_type}"
        
        if chunk.subheading:
            header += f" ({chunk.subheading})"
        
        # Check for tables
        has_tables = self.table_extractor.detect_tables(chunk.chunk_text)
        
        if has_tables:
            tables = self.table_extractor.extract_tables(chunk.chunk_text)
            if tables:
                result = f"{header}:\n{chunk.chunk_text}\n\n📊 TABLES:\n"
                for table in tables:
                    result += f"\n{table.to_formatted_text()}\n"
                return result
        
        return f"{header}:\n{chunk.chunk_text}"
    
    def _format_minimal(self, chunk: RetrievedChunk, citation_num: Optional[int] = None) -> str:
        """Minimal format - just content with simple attribution"""
        prefix = f"[{citation_num}] " if citation_num else ""
        suffix = f" ({chunk.company_name} {chunk.fiscal_year})"
        
        return f"{prefix}{chunk.chunk_text}{suffix}"
    
    def _create_citation(self, chunk: RetrievedChunk) -> str:
        """Create citation string"""
        citation = f"{chunk.company_name} 10-K ({chunk.fiscal_year}), "
        citation += f"{chunk.section} - {chunk.section_type}"
        
        if chunk.heading:
            citation += f", {chunk.heading}"
        
        return citation
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count.
        Rough approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4
    
    def build_rag_prompt(
        self,
        query: str,
        context: ContextWindow,
        instruction: str = None
    ) -> str:
        """
        Build complete RAG prompt with query and context.
        
        Args:
            query: User query
            context: Context window
            instruction: Custom instruction (uses default if None)
            
        Returns:
            Complete prompt string
        """
        if instruction is None:
            instruction = """You are a financial analyst assistant. Answer the question based on the provided context from SEC 10-K filings.

Instructions:
- Use ONLY information from the provided context
- Cite sources using [SOURCE X] numbers
- If the context doesn't contain enough information, say so
- Be specific and include relevant details
- Compare across companies/years when relevant"""
        
        prompt = f"""{instruction}

CONTEXT FROM 10-K FILINGS:
{context.formatted_context}

QUESTION:
{query}

ANSWER:"""
        
        return prompt
    
    def format_citations(self, citations: Dict[int, str]) -> str:
        """Format citations for display"""
        if not citations:
            return ""
        
        parts = ["Sources:"]
        for num, citation in sorted(citations.items()):
            parts.append(f"  [{num}] {citation}")
        
        return "\n".join(parts)


def test_context_builder():
    """Test context builder"""
    from semantic_retriever import SemanticRetriever
    
    print("Testing Context Builder\n")
    
    # Get some chunks
    retriever = SemanticRetriever()
    chunks = retriever.retrieve("What are the main AI initiatives?", top_k=3)
    retriever.close()
    
    # Build context
    builder = ContextBuilder()
    
    # Test different formats
    for style in ["detailed", "compact", "minimal"]:
        print(f"\n{'='*70}")
        print(f"FORMAT: {style.upper()}")
        print('='*70)
        
        context = builder.build_context(chunks, format_style=style)
        print(context.formatted_context[:500], "...")
        print(f"\nTokens: {context.total_tokens}")
        print(f"Chunks: {len(context.chunks_used)}")
        print(f"Truncated: {context.truncated}")
    
    # Test RAG prompt
    print(f"\n{'='*70}")
    print("RAG PROMPT")
    print('='*70)
    context = builder.build_context(chunks)
    prompt = builder.build_rag_prompt("What are companies doing with AI?", context)
    print(prompt[:800], "...")


if __name__ == "__main__":
    test_context_builder()
