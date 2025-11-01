"""
Database Loader - Load chunks and embeddings into Supabase
Handles batch insertion with error handling and validation.
"""

import numpy as np
from typing import List, Dict
from pathlib import Path
import sys
from tqdm import tqdm
import psycopg2
from psycopg2.extras import execute_values
from supabase import create_client, Client

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config
from json_processor import ChunkData


class DatabaseLoader:
    """Load embeddings into Supabase database"""
    
    def __init__(self, use_direct_postgres: bool = True):
        """
        Initialize database loader.
        
        Args:
            use_direct_postgres: Use direct PostgreSQL connection (faster for bulk)
                               If False, uses Supabase REST API
        """
        self.use_direct_postgres = use_direct_postgres
        self.batch_size = config.processing.db_batch_size
        
        print(f"🗄️  Initializing Database Loader")
        print(f"   Method: {'Direct PostgreSQL' if use_direct_postgres else 'Supabase REST API'}")
        print(f"   Batch size: {self.batch_size}")
        
        if use_direct_postgres:
            self.conn = self._create_postgres_connection()
            print(f"   ✅ PostgreSQL connection established")
        else:
            self.client = self._create_supabase_client()
            print(f"   ✅ Supabase client initialized")
        
        print()
    
    def _create_supabase_client(self) -> Client:
        """Create Supabase client"""
        try:
            client = create_client(
                config.database.supabase_url,
                config.database.supabase_service_key
            )
            return client
        except Exception as e:
            print(f"❌ Error creating Supabase client: {e}")
            raise
    
    def _create_postgres_connection(self):
        """Create direct PostgreSQL connection"""
        try:
            # Parse Supabase URL to get host
            # Format: https://xxxxx.supabase.co
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
            print(f"❌ Error creating PostgreSQL connection: {e}")
            print(f"   Make sure DB_PASSWORD is set in .env")
            raise
    
    def insert_batch_postgres(
        self,
        chunks: List[ChunkData],
        embeddings: np.ndarray
    ) -> int:
        """
        Insert batch using direct PostgreSQL connection (faster).
        
        Args:
            chunks: List of ChunkData objects
            embeddings: numpy array of embeddings
            
        Returns:
            Number of rows inserted
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch")
        
        # Prepare values
        values = []
        for chunk, embedding in zip(chunks, embeddings):
            values.append((
                chunk.company,
                chunk.company_name,
                chunk.ticker,
                chunk.fiscal_year,
                chunk.section,
                chunk.section_type,
                chunk.heading,
                chunk.subheading,
                chunk.chunk_text,
                chunk.word_count,
                embedding.tolist(),  # Convert numpy array to list
                chunk.source_file,
                chunk.chunk_index,
                chunk.chunk_total
            ))
        
        # SQL query
        insert_query = """
            INSERT INTO sec_10k_embeddings (
                company, company_name, ticker, fiscal_year,
                section, section_type, heading, subheading,
                chunk_text, word_count, embedding,
                source_file, chunk_index, chunk_total
            ) VALUES %s
            ON CONFLICT (company, fiscal_year, section, chunk_index) 
            DO NOTHING
        """
        
        try:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    insert_query,
                    values,
                    page_size=self.batch_size
                )
            self.conn.commit()
            return len(values)
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error inserting batch: {e}")
            raise
    
    def insert_batch_supabase(
        self,
        chunks: List[ChunkData],
        embeddings: np.ndarray
    ) -> int:
        """
        Insert batch using Supabase REST API.
        
        Args:
            chunks: List of ChunkData objects
            embeddings: numpy array of embeddings
            
        Returns:
            Number of rows inserted
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch")
        
        # Prepare records
        records = []
        for chunk, embedding in zip(chunks, embeddings):
            record = chunk.to_dict()
            record['embedding'] = embedding.tolist()
            records.append(record)
        
        try:
            response = self.client.table('sec_10k_embeddings').insert(records).execute()
            return len(records)
            
        except Exception as e:
            print(f"❌ Error inserting batch via Supabase API: {e}")
            raise
    
    def load_all(
        self,
        chunks: List[ChunkData],
        embeddings: np.ndarray,
        show_progress: bool = True
    ) -> Dict:
        """
        Load all chunks and embeddings to database.
        
        Args:
            chunks: List of ChunkData objects
            embeddings: numpy array of embeddings
            show_progress: Show progress bar
            
        Returns:
            Dictionary with statistics
        """
        total_chunks = len(chunks)
        total_inserted = 0
        total_errors = 0
        
        print(f"💾 Loading {total_chunks} chunks to database...")
        print(f"   Using batches of {self.batch_size}")
        print()
        
        # Process in batches
        for i in tqdm(range(0, total_chunks, self.batch_size), disable=not show_progress, desc="Inserting batches"):
            batch_end = min(i + self.batch_size, total_chunks)
            batch_chunks = chunks[i:batch_end]
            batch_embeddings = embeddings[i:batch_end]
            
            try:
                if self.use_direct_postgres:
                    inserted = self.insert_batch_postgres(batch_chunks, batch_embeddings)
                else:
                    inserted = self.insert_batch_supabase(batch_chunks, batch_embeddings)
                
                total_inserted += inserted
                
            except Exception as e:
                total_errors += len(batch_chunks)
                print(f"❌ Batch {i//self.batch_size + 1} failed: {e}")
        
        return {
            'total_chunks': total_chunks,
            'inserted': total_inserted,
            'errors': total_errors
        }
    
    def verify_insertion(self) -> Dict:
        """
        Verify data was inserted correctly.
        
        Returns:
            Dictionary with verification stats
        """
        print("\n🔍 Verifying insertion...")
        
        try:
            with self.conn.cursor() as cur:
                # Count total rows
                cur.execute("SELECT COUNT(*) FROM sec_10k_embeddings")
                total_rows = cur.fetchone()[0]
                
                # Count by company
                cur.execute("""
                    SELECT company_name, COUNT(*) 
                    FROM sec_10k_embeddings 
                    GROUP BY company_name 
                    ORDER BY company_name
                """)
                by_company = dict(cur.fetchall())
                
                # Count by year
                cur.execute("""
                    SELECT fiscal_year, COUNT(*) 
                    FROM sec_10k_embeddings 
                    GROUP BY fiscal_year 
                    ORDER BY fiscal_year
                """)
                by_year = dict(cur.fetchall())
                
                # Sample embedding check
                cur.execute("""
                    SELECT embedding 
                    FROM sec_10k_embeddings 
                    LIMIT 1
                """)
                sample_embedding = cur.fetchone()
                embedding_dim = len(sample_embedding[0]) if sample_embedding else 0
            
            return {
                'total_rows': total_rows,
                'by_company': by_company,
                'by_year': by_year,
                'embedding_dimension': embedding_dim
            }
            
        except Exception as e:
            print(f"❌ Error verifying insertion: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.use_direct_postgres and hasattr(self, 'conn'):
            self.conn.close()
            print("✅ Database connection closed")


def test_database_loader():
    """Test the database loader"""
    print("=" * 70)
    print("TESTING DATABASE LOADER")
    print("=" * 70)
    print()
    
    # Create test data
    test_chunks = [
        ChunkData(
            company="2024TEST_10K",
            company_name="TestCorp",
            ticker="TEST",
            fiscal_year=2024,
            source_file="test_file",
            section="Item 1",
            section_type="Business",
            heading="Test Heading",
            subheading="Test Subheading",
            chunk_text="This is a test chunk for database insertion testing.",
            word_count=10,
            chunk_index=1,
            chunk_total=1
        )
    ]
    
    # Create test embedding
    test_embeddings = np.random.rand(1, 384).astype(np.float32)
    test_embeddings = test_embeddings / np.linalg.norm(test_embeddings, axis=1, keepdims=True)
    
    # Initialize loader
    loader = DatabaseLoader(use_direct_postgres=True)
    
    # Test insertion
    print("Test: Inserting 1 test chunk...")
    stats = loader.load_all(test_chunks, test_embeddings, show_progress=False)
    
    print(f"\nInsertion Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verify
    verification = loader.verify_insertion()
    print(f"\nVerification:")
    for key, value in verification.items():
        print(f"  {key}: {value}")
    
    # Close
    loader.close()
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_database_loader()
