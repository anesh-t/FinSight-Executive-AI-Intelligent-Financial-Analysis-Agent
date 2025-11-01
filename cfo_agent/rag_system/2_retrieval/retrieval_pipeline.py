"""
Retrieval Pipeline - Orchestrates query routing, retrieval, and context building
Main interface for the retrieval system
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config
from query_router import QueryRouter, QueryAnalysis
from semantic_retriever import SemanticRetriever, RetrievedChunk
from context_builder import ContextBuilder, ContextWindow


@dataclass
class RetrievalResult:
    """Complete retrieval result"""
    query: str
    query_analysis: QueryAnalysis
    chunks: List[RetrievedChunk]
    context: ContextWindow
    rag_prompt: str
    metadata: Dict


class RetrievalPipeline:
    """Complete RAG retrieval pipeline"""
    
    def __init__(
        self,
        use_llm_routing: bool = True,
        enable_hybrid_search: bool = None,
        enable_context_expansion: bool = None
    ):
        """
        Initialize retrieval pipeline.
        
        Args:
            use_llm_routing: Use LLM for query routing
            enable_hybrid_search: Combine vector + keyword search
            enable_context_expansion: Retrieve neighboring chunks
        """
        print("🚀 Initializing Retrieval Pipeline...")
        print()
        
        # Configuration
        self.enable_hybrid = (enable_hybrid_search 
                             if enable_hybrid_search is not None 
                             else config.features.hybrid_search)
        self.enable_expansion = (enable_context_expansion 
                                if enable_context_expansion is not None 
                                else config.features.context_expansion)
        
        # Initialize components
        print("Loading query router...")
        self.router = QueryRouter(use_llm=use_llm_routing)
        
        print("Loading semantic retriever...")
        self.retriever = SemanticRetriever()
        
        print("Loading context builder...")
        self.context_builder = ContextBuilder()
        
        print("✅ Pipeline ready!")
        print()
    
    def process_query(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
        format_style: str = "detailed"
    ) -> RetrievalResult:
        """
        Process query through complete pipeline.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            min_similarity: Minimum similarity threshold
            format_style: Context format ("detailed", "compact", "minimal")
            
        Returns:
            Complete retrieval result
        """
        print(f"📝 Processing query: {query}")
        print()
        
        # Step 1: Route and analyze query
        print("🔍 Analyzing query...")
        analysis = self.router.route(query)
        self.router.print_analysis(analysis)
        print()
        
        # Step 2: Retrieve relevant chunks
        print(f"🔎 Retrieving top-{top_k} chunks...")
        
        if self.enable_hybrid and analysis.query_type in ["semantic", "hybrid"]:
            chunks = self.retriever.hybrid_search(
                query,
                top_k=top_k,
                companies=analysis.companies if analysis.companies else None,
                years=analysis.years if analysis.years else None,
                sections=analysis.sections if analysis.sections else None,
                min_similarity=min_similarity
            )
        else:
            chunks = self.retriever.retrieve(
                query,
                top_k=top_k,
                companies=analysis.companies if analysis.companies else None,
                years=analysis.years if analysis.years else None,
                sections=analysis.sections if analysis.sections else None,
                min_similarity=min_similarity
            )
        
        print(f"✅ Retrieved {len(chunks)} chunks")
        print()
        
        # Step 3: Expand context if enabled
        if self.enable_expansion and chunks:
            print("📖 Expanding context with neighboring chunks...")
            expanded_chunks = []
            for chunk in chunks[:3]:  # Expand top 3
                neighbors = self.retriever.expand_context(chunk, window_size=1)
                expanded_chunks.extend(neighbors)
            
            # Remove duplicates and re-sort by similarity
            seen_ids = set()
            unique_chunks = []
            for chunk in expanded_chunks:
                if chunk.chunk_id not in seen_ids:
                    seen_ids.add(chunk.chunk_id)
                    unique_chunks.append(chunk)
            
            chunks = sorted(unique_chunks, key=lambda c: c.similarity_score, reverse=True)[:top_k]
            print(f"✅ Context expanded to {len(chunks)} chunks")
            print()
        
        # Step 4: Build context
        print("📝 Building context...")
        context = self.context_builder.build_context(
            chunks,
            format_style=format_style
        )
        
        print(f"✅ Context built: {context.total_tokens} tokens, {len(context.chunks_used)} chunks")
        if context.truncated:
            print("⚠️  Context was truncated to fit token limit")
        print()
        
        # Step 5: Build RAG prompt
        rag_prompt = self.context_builder.build_rag_prompt(query, context)
        
        # Assemble result
        result = RetrievalResult(
            query=query,
            query_analysis=analysis,
            chunks=chunks,
            context=context,
            rag_prompt=rag_prompt,
            metadata={
                'hybrid_search': self.enable_hybrid,
                'context_expansion': self.enable_expansion,
                'chunks_retrieved': len(chunks),
                'tokens_used': context.total_tokens,
                'truncated': context.truncated
            }
        )
        
        return result
    
    def print_results(self, result: RetrievalResult, show_full_context: bool = False):
        """Pretty print retrieval results"""
        print("=" * 80)
        print("RETRIEVAL RESULTS")
        print("=" * 80)
        print()
        
        # Show metadata
        print("📊 Metadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")
        print()
        
        # Show chunks
        print(f"📄 Retrieved Chunks ({len(result.chunks)}):")
        print("-" * 80)
        for i, chunk in enumerate(result.chunks, 1):
            print(f"\n[{i}] {chunk.company_name} ({chunk.fiscal_year}) - {chunk.section_type}")
            print(f"    Similarity: {chunk.similarity_score:.4f}")
            print(f"    {chunk.heading}")
            if chunk.subheading:
                print(f"    → {chunk.subheading}")
            print(f"    Preview: {chunk.chunk_text[:150]}...")
        
        print()
        print("-" * 80)
        
        # Show context
        if show_full_context:
            print("\n📝 Formatted Context:")
            print("=" * 80)
            print(result.context.formatted_context)
            print("=" * 80)
        
        # Show citations
        if result.context.citations:
            print("\n📚 Citations:")
            print(self.context_builder.format_citations(result.context.citations))
        
        print()
    
    def close(self):
        """Close connections"""
        if hasattr(self, 'retriever'):
            self.retriever.close()
            print("✅ Pipeline closed")


def demo_pipeline():
    """Demo the complete pipeline"""
    print("=" * 80)
    print("RETRIEVAL PIPELINE DEMO")
    print("=" * 80)
    print()
    
    # Initialize pipeline
    pipeline = RetrievalPipeline(use_llm_routing=True)
    
    # Test queries
    test_queries = [
        "What are the main cybersecurity risks for tech companies?",
        "Compare AI strategies between Google and Microsoft",
        "What were Apple's supply chain challenges in 2023?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'#'*80}")
        print(f"TEST QUERY {i}/{len(test_queries)}")
        print(f"{'#'*80}\n")
        
        # Process query
        result = pipeline.process_query(query, top_k=3)
        
        # Show results
        pipeline.print_results(result, show_full_context=False)
        
        if i < len(test_queries):
            input("\nPress Enter for next query...")
    
    # Close
    pipeline.close()


if __name__ == "__main__":
    demo_pipeline()
