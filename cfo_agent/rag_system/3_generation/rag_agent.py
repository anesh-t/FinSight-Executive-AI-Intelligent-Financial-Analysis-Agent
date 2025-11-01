"""
RAG Agent - Complete end-to-end CFO Assistant
Query → Retrieve → Generate → Format → Answer
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config

# Import retrieval components
sys.path.insert(0, str(Path(__file__).parent.parent / '2_retrieval'))
from query_router import QueryRouter
from semantic_retriever import SemanticRetriever
from context_builder import ContextBuilder

# Import generation components
from response_generator import ResponseGenerator
from answer_formatter import AnswerFormatter, FormattedAnswer


class RAGAgent:
    """Complete CFO Assistant with end-to-end RAG pipeline"""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",  # Fast & cost-effective (6s avg) - use "gpt-4-turbo-preview" for higher quality
        use_llm_routing: bool = False,
        top_k: int = 5,
        max_tokens: int = 1500,  # Reduced from 2048 for speed (1500 = ~1125 words)
        verbose: bool = True
    ):
        """
        Initialize RAG Agent.
        
        Args:
            model: LLM model for answer generation
            use_llm_routing: Use LLM for query routing (slower but more accurate)
            top_k: Number of chunks to retrieve
            max_tokens: Maximum tokens in LLM response (lower = faster)
            verbose: Print progress messages
        """
        self.verbose = verbose
        self.top_k = top_k
        
        if verbose:
            print("=" * 80)
            print("🚀 INITIALIZING CFO ASSISTANT")
            print("=" * 80)
            print()
        
        # Initialize components
        if verbose:
            print("Loading query router...")
        self.router = QueryRouter(use_llm=use_llm_routing)
        
        if verbose:
            print("Loading semantic retriever...")
        self.retriever = SemanticRetriever()
        
        if verbose:
            print("Loading context builder...")
        self.context_builder = ContextBuilder()
        
        if verbose:
            print("Loading response generator...")
        self.response_generator = ResponseGenerator(model=model, max_tokens=max_tokens)
        
        if verbose:
            print("Loading answer formatter...")
        self.formatter = AnswerFormatter()
        
        if verbose:
            print()
            print("✅ CFO ASSISTANT READY!")
            print("=" * 80)
            print()
    
    def query(
        self,
        query: str,
        top_k: int = None,
        format_style: str = "detailed",
        return_metadata: bool = False
    ) -> FormattedAnswer:
        """
        Process query end-to-end and return answer.
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve (uses default if None)
            format_style: Context format ("detailed", "compact", "minimal")
            return_metadata: Return full metadata with answer
            
        Returns:
            FormattedAnswer with complete response
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"📝 Query: {query}")
            print()
        
        # Step 1: Route query
        if self.verbose:
            print("🔍 Step 1: Analyzing query...")
        
        analysis = self.router.route(query)
        
        if self.verbose:
            print(f"   Type: {analysis.query_type}")
            if analysis.companies:
                print(f"   Companies: {', '.join(analysis.companies)}")
            if analysis.years:
                print(f"   Years: {', '.join(map(str, analysis.years))}")
            if analysis.sections:
                print(f"   Sections: {', '.join(analysis.sections[:2])}...")
            print()
        
        # Step 2: Retrieve relevant chunks
        if self.verbose:
            print(f"🔎 Step 2: Retrieving top-{top_k or self.top_k} chunks...")
        
        # Special handling for comparison queries with multiple companies
        if analysis.companies and len(analysis.companies) > 1:
            # Retrieve separately for each company to ensure balanced representation
            chunks = []
            per_company = (top_k or self.top_k) // len(analysis.companies)
            
            if self.verbose:
                print(f"   Comparison query detected: retrieving {per_company} chunks per company")
            
            for company in analysis.companies:
                company_chunks = self.retriever.retrieve(
                    query=query,
                    top_k=per_company,
                    companies=[company],
                    years=analysis.years if analysis.years else None,
                    sections=analysis.sections if analysis.sections else None,
                    min_similarity=0.3
                )
                chunks.extend(company_chunks)
                
                if self.verbose:
                    print(f"   ✅ {company}: {len(company_chunks)} chunks")
        else:
            # Single company or no company filter - normal retrieval
            chunks = self.retriever.retrieve(
                query=query,
                top_k=top_k or self.top_k,
                companies=analysis.companies if analysis.companies else None,
                years=analysis.years if analysis.years else None,
                sections=analysis.sections if analysis.sections else None,
                min_similarity=0.3
            )
        
        if self.verbose:
            print(f"   ✅ Total retrieved: {len(chunks)} chunks")
            print()
        
        # Step 3: Build context
        if self.verbose:
            print("📝 Step 3: Building context...")
        
        context = self.context_builder.build_context(
            chunks,
            format_style=format_style
        )
        
        if self.verbose:
            print(f"   ✅ Context: {context.total_tokens} tokens, {len(context.chunks_used)} chunks")
            print()
        
        # Step 4: Generate answer
        if self.verbose:
            print("🤖 Step 4: Generating CFO-level analysis...")
        
        answer = self.response_generator.generate(query, context)
        
        if self.verbose:
            print(f"   ✅ Answer generated: {answer.llm_response.total_tokens} tokens")
            print()
        
        # Step 5: Format answer
        if self.verbose:
            print("📄 Step 5: Formatting response...")
        
        formatted = self.formatter.format(answer)
        
        # Add retrieval metadata
        formatted.metadata['retrieval_chunks'] = len(chunks)
        formatted.metadata['context_tokens'] = context.total_tokens
        formatted.metadata['total_latency'] = time.time() - start_time
        
        if self.verbose:
            print(f"   ✅ Complete!")
            print()
            print("=" * 80)
            print()
        
        return formatted
    
    def query_simple(self, query: str) -> str:
        """
        Simple query interface - returns just the answer text.
        
        Args:
            query: User question
            
        Returns:
            Answer text
        """
        result = self.query(query)
        return result.text
    
    def close(self):
        """Close connections"""
        if hasattr(self, 'retriever'):
            self.retriever.close()
            if self.verbose:
                print("✅ CFO Assistant closed")


def demo():
    """Quick demo"""
    print("\n")
    print("=" * 80)
    print("CFO ASSISTANT DEMO")
    print("=" * 80)
    print("\n")
    
    agent = RAGAgent(model="gpt-4", verbose=True)
    
    # Test query
    query = "What are the main cybersecurity risks for tech companies?"
    
    result = agent.query(query, top_k=3)
    result.display()
    
    agent.close()


if __name__ == "__main__":
    demo()
