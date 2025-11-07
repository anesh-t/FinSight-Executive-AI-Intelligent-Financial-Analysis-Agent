"""
Table-Specific Retriever - Enhanced retrieval for financial tables from 10-K
"""

import sys
from pathlib import Path
from typing import List, Optional
import re

sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))
from semantic_retriever import SemanticRetriever, RetrievedChunk


class TableRetriever:
    """
    Enhanced retriever specifically for extracting financial tables from 10-K filings.
    Uses multiple strategies to improve table retrieval accuracy.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize table retriever"""
        self.verbose = verbose
        self.retriever = SemanticRetriever()
        
        # Table-specific keywords to boost retrieval
        self.table_indicators = [
            'were as follows',
            'in millions',
            'in thousands',
            'dollars in millions',
            'the following table',
            'as follows:',
            'breakdown',
            'by segment',
            'by category',
            'by product',
            'by region',
            'Products',
            'Services',
            '$'
        ]
        
        if self.verbose:
            print("✅ Table Retriever initialized")
    
    def retrieve_table(
        self,
        query: str,
        company: Optional[str] = None,
        year: Optional[int] = None,
        top_k: int = 10  # Retrieve more chunks to find tables
    ) -> List[RetrievedChunk]:
        """
        Retrieve chunks containing financial tables.
        
        Strategy:
        1. Enhance query with table-specific keywords
        2. Retrieve more chunks (top_k=10)
        3. Re-rank based on table indicators
        4. Return top chunks with highest table likelihood
        
        Args:
            query: User query
            company: Optional company filter (e.g., "Apple")
            year: Optional year filter (e.g., 2019)
            top_k: Number of chunks to retrieve initially
            
        Returns:
            List of chunks ranked by table likelihood
        """
        # Step 1: Enhance query with table keywords
        enhanced_query = self._enhance_query_for_tables(query)
        
        if self.verbose:
            print(f"Original query: {query}")
            print(f"Enhanced query: {enhanced_query}")
        
        # Step 2: Retrieve chunks with filters
        companies = [company] if company else None
        years = [year] if year else None
        
        chunks = self.retriever.retrieve(
            query=enhanced_query,
            top_k=top_k,
            companies=companies,
            years=years,
            min_similarity=0.5  # Lower threshold to get more candidates
        )
        
        if self.verbose:
            print(f"Retrieved {len(chunks)} chunks")
        
        # Step 3: Re-rank based on table indicators
        ranked_chunks = self._rerank_by_table_likelihood(chunks)
        
        # Step 4: Return top 5 most likely table chunks
        return ranked_chunks[:5]
    
    def _enhance_query_for_tables(self, query: str) -> str:
        """
        Enhance query with table-specific keywords to improve retrieval.
        
        Examples:
        - "Show gross margin breakdown" → "Show gross margin breakdown table by segment in millions"
        - "Apple revenue by product" → "Apple revenue by product category table breakdown"
        """
        enhanced = query
        
        # Add table-specific terms if not present
        if 'table' not in query.lower():
            enhanced += " table"
        
        if 'breakdown' not in query.lower() and 'by' in query.lower():
            enhanced += " breakdown"
        
        # Add "in millions" for financial queries
        if any(term in query.lower() for term in ['revenue', 'margin', 'income', 'profit', 'sales']):
            if 'million' not in query.lower():
                enhanced += " in millions"
        
        # Add "by segment" for breakdown queries
        if any(term in query.lower() for term in ['products', 'services', 'segment', 'category']):
            if 'segment' not in query.lower():
                enhanced += " by segment"
        
        return enhanced
    
    def _rerank_by_table_likelihood(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Re-rank chunks based on likelihood of containing tables.
        
        Scoring factors:
        1. Presence of table indicators (e.g., "were as follows", "in millions")
        2. Presence of dollar signs ($)
        3. Presence of numbers and percentages
        4. Presence of segment keywords (Products, Services)
        5. Length (tables tend to be in longer chunks)
        """
        scored_chunks = []
        
        for chunk in chunks:
            score = chunk.similarity_score  # Start with semantic similarity
            text = chunk.chunk_text.lower()
            
            # Boost for table indicators
            for indicator in self.table_indicators:
                if indicator.lower() in text:
                    score += 0.1
            
            # Boost for dollar signs (strong indicator of financial tables)
            dollar_count = text.count('$')
            score += min(dollar_count * 0.05, 0.3)  # Cap at 0.3
            
            # Boost for numbers (tables have many numbers)
            number_count = len(re.findall(r'\d+,?\d*', text))
            score += min(number_count * 0.01, 0.2)  # Cap at 0.2
            
            # Boost for percentages
            percentage_count = text.count('%')
            score += min(percentage_count * 0.05, 0.2)  # Cap at 0.2
            
            # Boost for segment keywords
            if 'products' in text and 'services' in text:
                score += 0.3  # Strong indicator of segment breakdown
            
            # Boost for longer chunks (tables tend to be detailed)
            if chunk.word_count > 200:
                score += 0.1
            
            # Boost for specific sections that contain tables
            if chunk.section_type in ['financial_statements', 'md&a']:
                score += 0.15
            
            scored_chunks.append((score, chunk))
        
        # Sort by score (descending)
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        if self.verbose:
            print("\nTop 5 chunks by table likelihood:")
            for i, (score, chunk) in enumerate(scored_chunks[:5], 1):
                print(f"{i}. Score: {score:.2f} | Similarity: {chunk.similarity_score:.2f} | "
                      f"Words: {chunk.word_count} | Section: {chunk.section_type}")
                print(f"   Preview: {chunk.chunk_text[:100]}...")
        
        # Return chunks sorted by table likelihood
        return [chunk for score, chunk in scored_chunks]
    
    def close(self):
        """Close database connection"""
        if hasattr(self.retriever, 'conn'):
            self.retriever.conn.close()


def test_table_retriever():
    """Test the table retriever"""
    print("=" * 80)
    print("TESTING TABLE RETRIEVER")
    print("=" * 80)
    
    retriever = TableRetriever(verbose=True)
    
    # Test query
    query = "Show Apple's gross margin breakdown for products and services"
    print(f"\nQuery: {query}\n")
    
    chunks = retriever.retrieve_table(
        query=query,
        company="Apple",
        year=2019,
        top_k=10
    )
    
    print("\n" + "=" * 80)
    print("TOP RETRIEVED CHUNK:")
    print("=" * 80)
    if chunks:
        top_chunk = chunks[0]
        print(f"Company: {top_chunk.company_name}")
        print(f"Year: {top_chunk.fiscal_year}")
        print(f"Section: {top_chunk.section_type}")
        print(f"Similarity: {top_chunk.similarity_score:.3f}")
        print(f"\nText:\n{top_chunk.chunk_text[:1000]}")
        
        # Check if it has the table data
        if "Products" in top_chunk.chunk_text and "Services" in top_chunk.chunk_text:
            if "68,887" in top_chunk.chunk_text or "68887" in top_chunk.chunk_text:
                print("\n✅ SUCCESS! Found the Products/Services breakdown table!")
            else:
                print("\n⚠️ Found Products/Services mention but not the exact table")
        else:
            print("\n❌ Did not find Products/Services breakdown")
    
    retriever.close()


if __name__ == "__main__":
    test_table_retriever()
