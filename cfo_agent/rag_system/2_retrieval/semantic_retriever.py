"""
Semantic Retrieval Engine - Advanced vector search with filtering and re-ranking
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config

# Import embedding generator
sys.path.insert(0, str(Path(__file__).parent.parent / '1_ingestion'))
from embedding_generator import EmbeddingGenerator


@dataclass
class RetrievedChunk:
    """Single retrieved chunk with metadata"""
    chunk_id: int
    company_name: str
    ticker: str
    fiscal_year: int
    section: str
    section_type: str
    heading: str
    subheading: Optional[str]
    chunk_text: str
    word_count: int
    similarity_score: float
    chunk_index: Optional[int]
    chunk_total: Optional[int]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'chunk_id': self.chunk_id,
            'company_name': self.company_name,
            'ticker': self.ticker,
            'fiscal_year': self.fiscal_year,
            'section': self.section,
            'section_type': self.section_type,
            'heading': self.heading,
            'subheading': self.subheading,
            'chunk_text': self.chunk_text,
            'word_count': self.word_count,
            'similarity_score': self.similarity_score,
            'chunk_index': self.chunk_index,
            'chunk_total': self.chunk_total
        }


class SemanticRetriever:
    """Advanced semantic retrieval with filters and optimizations"""
    
    def __init__(self):
        """Initialize retriever"""
        print("🔍 Initializing Semantic Retriever...")
        
        # Load embedding generator
        self.embedder = EmbeddingGenerator()
        
        # Connect to database
        self.conn = self._create_connection()
        
        print("✅ Retriever ready!")
        print()
    
    def _create_connection(self):
        """Create PostgreSQL connection using Supabase"""
        try:
            # Use direct Supabase connection with hardcoded password from SUPABASE_DB_URL
            conn = psycopg2.connect(
                host='db.ikhrfgywojsrvxgdojxd.supabase.co',
                port=5432,
                database='postgres',
                user='postgres',
                password='asntrbdrhbcsdgjkt'
            )
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        companies: Optional[List[str]] = None,
        years: Optional[List[int]] = None,
        sections: Optional[List[str]] = None,
        min_similarity: float = 0.0,
        diversity_threshold: float = 0.9
    ) -> List[RetrievedChunk]:
        """
        Semantic search with filters.
        
        Args:
            query: Search query
            top_k: Number of results
            companies: Filter by companies
            years: Filter by years
            sections: Filter by section types
            min_similarity: Minimum similarity threshold
            diversity_threshold: Remove near-duplicates above this similarity
            
        Returns:
            List of retrieved chunks
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_single_embedding(query)
        
        # Build SQL with filters
        sql = """
            SELECT 
                id as chunk_id,
                company_name,
                ticker,
                fiscal_year,
                section,
                section_type,
                heading,
                subheading,
                chunk_text,
                word_count,
                chunk_index,
                chunk_total,
                1 - (embedding <=> %s::vector) as similarity_score
            FROM sec_10k_embeddings
            WHERE 1=1
        """
        
        params = [query_embedding.tolist()]
        
        # Add filters
        if companies:
            placeholders = ','.join(['%s'] * len(companies))
            sql += f" AND company_name IN ({placeholders})"
            params.extend(companies)
        
        if years:
            placeholders = ','.join(['%s'] * len(years))
            sql += f" AND fiscal_year IN ({placeholders})"
            params.extend(years)
        
        if sections:
            placeholders = ','.join(['%s'] * len(sections))
            sql += f" AND section_type IN ({placeholders})"
            params.extend(sections)
        
        # Add similarity filter
        if min_similarity > 0:
            sql += " AND (1 - (embedding <=> %s::vector)) >= %s"
            params.extend([query_embedding.tolist(), min_similarity])
        
        # Order and limit (fetch more for diversity filtering)
        fetch_k = top_k * 3  # Fetch 3x for diversity filtering
        sql += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([query_embedding.tolist(), fetch_k])
        
        # Execute query
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            results = cur.fetchall()
        
        # Convert to RetrievedChunk objects
        chunks = [
            RetrievedChunk(**dict(row))
            for row in results
        ]
        
        # Apply diversity filtering
        if diversity_threshold < 1.0:
            chunks = self._apply_diversity_filter(chunks, diversity_threshold)
        
        # Return top-k
        return chunks[:top_k]
    
    def _apply_diversity_filter(
        self,
        chunks: List[RetrievedChunk],
        threshold: float
    ) -> List[RetrievedChunk]:
        """
        Remove near-duplicate chunks based on text similarity.
        Keeps chunks that are sufficiently different from already selected ones.
        """
        if not chunks:
            return chunks
        
        selected = [chunks[0]]  # Always keep the top result
        
        for chunk in chunks[1:]:
            # Check similarity with all selected chunks
            is_diverse = True
            for selected_chunk in selected:
                # Simple text-based diversity check
                # Could be enhanced with embedding similarity
                if (chunk.company_name == selected_chunk.company_name and
                    chunk.section_type == selected_chunk.section_type and
                    chunk.fiscal_year == selected_chunk.fiscal_year and
                    chunk.heading == selected_chunk.heading):
                    # Very similar context, check text overlap
                    text_similarity = self._text_jaccard_similarity(
                        chunk.chunk_text,
                        selected_chunk.chunk_text
                    )
                    if text_similarity > threshold:
                        is_diverse = False
                        break
            
            if is_diverse:
                selected.append(chunk)
        
        return selected
    
    def _text_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def expand_context(
        self,
        chunk: RetrievedChunk,
        window_size: int = 1
    ) -> List[RetrievedChunk]:
        """
        Expand context by retrieving neighboring chunks.
        
        Args:
            chunk: Main chunk
            window_size: Number of chunks before/after
            
        Returns:
            List including main chunk and neighbors
        """
        if chunk.chunk_index is None or chunk.chunk_total is None:
            return [chunk]
        
        # Calculate neighbor indices
        start_idx = max(1, chunk.chunk_index - window_size)
        end_idx = min(chunk.chunk_total, chunk.chunk_index + window_size)
        
        # Query for neighbors
        sql = """
            SELECT 
                id as chunk_id,
                company_name, ticker, fiscal_year,
                section, section_type, heading, subheading,
                chunk_text, word_count, chunk_index, chunk_total,
                0.0 as similarity_score
            FROM sec_10k_embeddings
            WHERE company = %s
              AND fiscal_year = %s
              AND section = %s
              AND chunk_index BETWEEN %s AND %s
            ORDER BY chunk_index
        """
        
        params = [
            f"{chunk.fiscal_year}{chunk.ticker}_10K",  # company field format
            chunk.fiscal_year,
            chunk.section,
            start_idx,
            end_idx
        ]
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            results = cur.fetchall()
        
        return [RetrievedChunk(**dict(row)) for row in results]
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
        **filters
    ) -> List[RetrievedChunk]:
        """
        Hybrid search combining vector and keyword search.
        
        Args:
            query: Search query
            top_k: Number of results
            vector_weight: Weight for vector search (1-weight for keyword)
            **filters: Additional filters
            
        Returns:
            Re-ranked results combining both methods
        """
        # Vector search
        vector_results = self.retrieve(query, top_k=top_k*2, **filters)
        
        # Keyword search using full-text search
        keyword_results = self._keyword_search(query, top_k=top_k*2, **filters)
        
        # Merge and re-rank
        combined = self._merge_results(
            vector_results,
            keyword_results,
            vector_weight=vector_weight
        )
        
        return combined[:top_k]
    
    def _keyword_search(
        self,
        query: str,
        top_k: int = 5,
        **filters
    ) -> List[RetrievedChunk]:
        """Keyword-based search using PostgreSQL full-text search"""
        
        # Build query
        sql = """
            SELECT 
                id as chunk_id,
                company_name, ticker, fiscal_year,
                section, section_type, heading, subheading,
                chunk_text, word_count, chunk_index, chunk_total,
                ts_rank(search_vector, plainto_tsquery('english', %s)) as similarity_score
            FROM sec_10k_embeddings
            WHERE search_vector @@ plainto_tsquery('english', %s)
        """
        
        params = [query, query]
        
        # Add filters (simplified for this example)
        if 'companies' in filters and filters['companies']:
            placeholders = ','.join(['%s'] * len(filters['companies']))
            sql += f" AND company_name IN ({placeholders})"
            params.extend(filters['companies'])
        
        sql += " ORDER BY similarity_score DESC LIMIT %s"
        params.append(top_k)
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
            
            return [RetrievedChunk(**dict(row)) for row in results]
        except Exception as e:
            print(f"⚠️  Keyword search failed: {e}")
            return []
    
    def _merge_results(
        self,
        vector_results: List[RetrievedChunk],
        keyword_results: List[RetrievedChunk],
        vector_weight: float = 0.7
    ) -> List[RetrievedChunk]:
        """Merge and re-rank results from vector and keyword search"""
        
        # Create score dictionary
        scores = {}
        
        # Add vector scores
        for i, chunk in enumerate(vector_results):
            key = chunk.chunk_id
            rank_score = 1.0 - (i / len(vector_results))  # Normalize rank
            scores[key] = {
                'chunk': chunk,
                'vector_score': chunk.similarity_score,
                'keyword_score': 0.0,
                'rank_score': rank_score
            }
        
        # Add keyword scores
        for i, chunk in enumerate(keyword_results):
            key = chunk.chunk_id
            rank_score = 1.0 - (i / len(keyword_results))
            if key in scores:
                scores[key]['keyword_score'] = chunk.similarity_score
                scores[key]['rank_score'] = (scores[key]['rank_score'] + rank_score) / 2
            else:
                scores[key] = {
                    'chunk': chunk,
                    'vector_score': 0.0,
                    'keyword_score': chunk.similarity_score,
                    'rank_score': rank_score
                }
        
        # Calculate combined scores
        for key in scores:
            v_score = scores[key]['vector_score']
            k_score = scores[key]['keyword_score']
            # Normalize keyword score to 0-1 range
            k_score_norm = min(k_score, 1.0) if k_score > 0 else 0.0
            
            combined = (vector_weight * v_score + 
                       (1 - vector_weight) * k_score_norm)
            scores[key]['combined_score'] = combined
            scores[key]['chunk'].similarity_score = combined
        
        # Sort by combined score
        sorted_chunks = sorted(
            [s['chunk'] for s in scores.values()],
            key=lambda c: c.similarity_score,
            reverse=True
        )
        
        return sorted_chunks
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    # Quick test
    retriever = SemanticRetriever()
    
    query = "What are the main cybersecurity risks?"
    print(f"Testing query: {query}\n")
    
    results = retriever.retrieve(query, top_k=3)
    
    for i, chunk in enumerate(results, 1):
        print(f"\n{'='*70}")
        print(f"Result #{i}")
        print(f"{'='*70}")
        print(f"Company: {chunk.company_name} ({chunk.fiscal_year})")
        print(f"Section: {chunk.section_type}")
        print(f"Similarity: {chunk.similarity_score:.4f}")
        print(f"Text: {chunk.chunk_text[:200]}...")
    
    retriever.close()
