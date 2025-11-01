"""
Test Semantic Search - Demonstrate vector database search capabilities
Query your 10-K data with natural language
"""

import sys
from pathlib import Path
import numpy as np
from typing import List, Dict
import psycopg2
from psycopg2.extras import RealDictCursor

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
from foundation.config import config

# Import from 1_ingestion module
sys.path.insert(0, str(Path(__file__).parent / '1_ingestion'))
from embedding_generator import EmbeddingGenerator


class SemanticSearchTester:
    """Test semantic search on 10-K embeddings"""
    
    def __init__(self):
        """Initialize search tester"""
        print("🔍 Initializing Semantic Search Tester")
        print()
        
        # Load embedding generator
        print("Loading embedding model...")
        self.embedder = EmbeddingGenerator()
        
        # Connect to database
        print("Connecting to database...")
        self.conn = self._create_connection()
        print("✅ Ready to search!")
        print()
    
    def _create_connection(self):
        """Create PostgreSQL connection"""
        try:
            # Parse Supabase URL
            host = config.database.supabase_url.replace('https://', '').replace('.supabase.co', '')
            host = f"db.{host}.supabase.co"
            
            conn = psycopg2.connect(
                host=host,
                port=5432,
                database='postgres',
                user='postgres',
                password=config.database.db_password
            )
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        company_filter: str = None,
        year_filter: int = None,
        section_filter: str = None
    ) -> List[Dict]:
        """
        Semantic search for relevant chunks.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            company_filter: Filter by company name (e.g., "Apple")
            year_filter: Filter by fiscal year (e.g., 2024)
            section_filter: Filter by section type (e.g., "Risk Factors")
            
        Returns:
            List of matching chunks with metadata and similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_single_embedding(query)
        
        # Build SQL query with filters
        sql = """
            SELECT 
                company_name,
                ticker,
                fiscal_year,
                section,
                section_type,
                heading,
                subheading,
                chunk_text,
                word_count,
                1 - (embedding <=> %s::vector) as similarity
            FROM sec_10k_embeddings
            WHERE 1=1
        """
        
        params = [query_embedding.tolist()]
        
        # Add filters
        if company_filter:
            sql += " AND company_name = %s"
            params.append(company_filter)
        
        if year_filter:
            sql += " AND fiscal_year = %s"
            params.append(year_filter)
        
        if section_filter:
            sql += " AND section_type = %s"
            params.append(section_filter)
        
        sql += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.extend([query_embedding.tolist(), top_k])
        
        # Execute query
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            results = cur.fetchall()
        
        return [dict(row) for row in results]
    
    def print_results(self, query: str, results: List[Dict]):
        """Pretty print search results"""
        print("=" * 80)
        print(f"🔎 QUERY: {query}")
        print("=" * 80)
        print()
        
        if not results:
            print("❌ No results found")
            return
        
        for i, result in enumerate(results, 1):
            print(f"📄 RESULT #{i}")
            print("-" * 80)
            print(f"Company:    {result['company_name']} ({result['ticker']}) - {result['fiscal_year']}")
            print(f"Section:    {result['section']} - {result['section_type']}")
            print(f"Heading:    {result['heading']}")
            if result['subheading']:
                print(f"Subheading: {result['subheading']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Words:      {result['word_count']}")
            print()
            
            # Print text preview (first 300 chars)
            text = result['chunk_text']
            preview = text[:300] + "..." if len(text) > 300 else text
            print(f"Text:\n{preview}")
            print()
        
        print("=" * 80)
        print()
    
    def run_demo_queries(self):
        """Run a set of demo queries to showcase capabilities"""
        print("=" * 80)
        print("SEMANTIC SEARCH DEMO - 10-K FILINGS DATABASE")
        print("=" * 80)
        print()
        print("Database Stats:")
        
        # Get stats
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sec_10k_embeddings")
            total = cur.fetchone()[0]
            print(f"  Total chunks: {total:,}")
            
            cur.execute("SELECT COUNT(DISTINCT company_name) FROM sec_10k_embeddings")
            companies = cur.fetchone()[0]
            print(f"  Companies: {companies}")
            
            cur.execute("SELECT COUNT(DISTINCT fiscal_year) FROM sec_10k_embeddings")
            years = cur.fetchone()[0]
            print(f"  Years: {years}")
        
        print()
        print("Running demo queries...")
        print()
        
        # Demo queries
        demo_queries = [
            {
                "query": "What are the main business risks?",
                "filters": {"top_k": 3}
            },
            {
                "query": "AI and machine learning investments",
                "filters": {"top_k": 3, "year_filter": 2024}
            },
            {
                "query": "regulatory challenges and compliance",
                "filters": {"top_k": 3, "company_filter": "Meta"}
            },
            {
                "query": "cloud computing revenue growth",
                "filters": {"top_k": 3, "company_filter": "Amazon"}
            },
            {
                "query": "supply chain disruptions",
                "filters": {"top_k": 3, "company_filter": "Apple"}
            }
        ]
        
        for demo in demo_queries:
            results = self.search(demo["query"], **demo["filters"])
            self.print_results(demo["query"], results)
            input("Press Enter to continue to next query...")
            print()
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("=" * 80)
        print("INTERACTIVE SEMANTIC SEARCH")
        print("=" * 80)
        print()
        print("Enter your queries to search the 10-K database.")
        print("Commands:")
        print("  - Type your query and press Enter")
        print("  - 'quit' or 'exit' to stop")
        print("  - 'demo' to run demo queries")
        print()
        
        while True:
            try:
                query = input("🔍 Query: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if query.lower() == 'demo':
                    self.run_demo_queries()
                    continue
                
                # Parse filters from query (simple approach)
                company_filter = None
                year_filter = None
                top_k = 5
                
                # Check for company mentions
                for company in ['Amazon', 'Apple', 'Google', 'Meta', 'Microsoft']:
                    if company.lower() in query.lower():
                        company_filter = company
                        break
                
                # Check for year mentions
                for year in range(2019, 2025):
                    if str(year) in query:
                        year_filter = year
                        break
                
                # Execute search
                results = self.search(
                    query,
                    top_k=top_k,
                    company_filter=company_filter,
                    year_filter=year_filter
                )
                
                self.print_results(query, results)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("✅ Database connection closed")


def main():
    """Main entry point"""
    try:
        tester = SemanticSearchTester()
        
        # Check command line args
        if len(sys.argv) > 1:
            if sys.argv[1] == 'demo':
                tester.run_demo_queries()
            else:
                # Run single query from command line
                query = ' '.join(sys.argv[1:])
                results = tester.search(query)
                tester.print_results(query, results)
        else:
            # Interactive mode
            tester.interactive_mode()
        
        tester.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
