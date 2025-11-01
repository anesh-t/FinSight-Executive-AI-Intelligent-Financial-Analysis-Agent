"""
Main Ingestion Pipeline - Orchestrates the complete ingestion process
Processes JSON files → Generates embeddings → Loads to database
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config
from json_processor import JSONProcessor
from embedding_generator import EmbeddingGenerator
from database_loader import DatabaseLoader


class IngestionPipeline:
    """Complete ingestion pipeline orchestrator"""
    
    def __init__(self):
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'files_processed': 0,
            'chunks_extracted': 0,
            'embeddings_generated': 0,
            'rows_inserted': 0,
            'errors': []
        }
    
    def run(self):
        """Execute the complete ingestion pipeline"""
        print("=" * 80)
        print("RAG SYSTEM - DATA INGESTION PIPELINE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.stats['start_time'] = time.time()
        
        try:
            # Step 1: Process JSON files
            print("STEP 1: PROCESSING JSON FILES")
            print("-" * 80)
            chunks = self._process_json_files()
            
            if not chunks:
                print("❌ No chunks extracted. Aborting.")
                return
            
            print()
            
            # Step 2: Generate embeddings
            print("STEP 2: GENERATING EMBEDDINGS")
            print("-" * 80)
            embeddings = self._generate_embeddings(chunks)
            print()
            
            # Step 3: Load to database
            print("STEP 3: LOADING TO DATABASE")
            print("-" * 80)
            self._load_to_database(chunks, embeddings)
            print()
            
            # Step 4: Verify
            print("STEP 4: VERIFICATION")
            print("-" * 80)
            self._verify_data()
            print()
            
        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            self.stats['errors'].append(str(e))
            raise
        
        finally:
            self.stats['end_time'] = time.time()
            self.stats['duration_seconds'] = self.stats['end_time'] - self.stats['start_time']
            self._print_final_summary()
    
    def _process_json_files(self):
        """Step 1: Process JSON files"""
        processor = JSONProcessor(config.paths.json_folder)
        chunks = processor.process_all_files()
        
        self.stats['files_processed'] = processor.stats['files_processed']
        self.stats['chunks_extracted'] = processor.stats['chunks_extracted']
        self.stats['errors'].extend(processor.stats['errors'])
        
        processor.print_stats()
        
        return chunks
    
    def _generate_embeddings(self, chunks):
        """Step 2: Generate embeddings"""
        generator = EmbeddingGenerator()
        
        # Extract text from chunks
        texts = [chunk.chunk_text for chunk in chunks]
        
        print(f"📊 Generating embeddings for {len(texts)} chunks...")
        print(f"   Model: {generator.model_name}")
        print(f"   Dimension: {generator.dimension}")
        print()
        
        # Generate embeddings
        embeddings = generator.generate_embeddings(texts, show_progress=True)
        
        # Verify
        stats = generator.verify_embeddings(embeddings)
        
        print(f"\n✅ Embeddings generated!")
        print(f"   Shape: {stats['shape']}")
        print(f"   Mean norm: {stats['mean_norm']:.4f}")
        print(f"   Contains NaN: {stats['contains_nan']}")
        print(f"   Contains Inf: {stats['contains_inf']}")
        
        self.stats['embeddings_generated'] = len(embeddings)
        
        return embeddings
    
    def _load_to_database(self, chunks, embeddings):
        """Step 3: Load to database"""
        loader = DatabaseLoader(use_direct_postgres=True)
        
        try:
            load_stats = loader.load_all(chunks, embeddings, show_progress=True)
            
            self.stats['rows_inserted'] = load_stats['inserted']
            if load_stats['errors'] > 0:
                self.stats['errors'].append(f"{load_stats['errors']} chunks failed to insert")
            
            print(f"\n✅ Database loading complete!")
            print(f"   Total chunks: {load_stats['total_chunks']}")
            print(f"   Inserted: {load_stats['inserted']}")
            print(f"   Errors: {load_stats['errors']}")
            
        finally:
            loader.close()
    
    def _verify_data(self):
        """Step 4: Verify data"""
        loader = DatabaseLoader(use_direct_postgres=True)
        
        try:
            verification = loader.verify_insertion()
            
            print(f"📊 Database Statistics:")
            print(f"   Total rows: {verification.get('total_rows', 0):,}")
            print(f"   Embedding dimension: {verification.get('embedding_dimension', 0)}")
            
            print(f"\n📈 By Company:")
            for company, count in verification.get('by_company', {}).items():
                print(f"   {company}: {count:,} chunks")
            
            print(f"\n📅 By Year:")
            for year, count in verification.get('by_year', {}).items():
                print(f"   {year}: {count:,} chunks")
            
        finally:
            loader.close()
    
    def _print_final_summary(self):
        """Print final pipeline summary"""
        print()
        print("=" * 80)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 80)
        
        duration_min = self.stats['duration_seconds'] / 60
        
        print(f"⏱️  Duration: {duration_min:.2f} minutes ({self.stats['duration_seconds']:.1f} seconds)")
        print()
        print(f"📁 Files Processed: {self.stats['files_processed']}")
        print(f"📦 Chunks Extracted: {self.stats['chunks_extracted']:,}")
        print(f"🧮 Embeddings Generated: {self.stats['embeddings_generated']:,}")
        print(f"💾 Rows Inserted: {self.stats['rows_inserted']:,}")
        print()
        
        if self.stats['chunks_extracted'] > 0:
            chunks_per_sec = self.stats['chunks_extracted'] / self.stats['duration_seconds']
            print(f"🚀 Processing Speed: {chunks_per_sec:.1f} chunks/second")
            print()
        
        # Estimate database size
        # Rough calculation: each row ≈ 6KB (4KB text + 1.5KB embedding + metadata)
        estimated_mb = (self.stats['rows_inserted'] * 6) / 1024
        print(f"💽 Estimated Database Size: ~{estimated_mb:.1f} MB")
        print()
        
        if self.stats['errors']:
            print(f"⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5
                print(f"   - {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more")
            print()
        
        if self.stats['rows_inserted'] > 0:
            print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("❌ PIPELINE COMPLETED WITH ERRORS")
        
        print("=" * 80)
        print()
        
        # Next steps
        if self.stats['rows_inserted'] > 0:
            print("🎯 NEXT STEPS:")
            print("   1. Test semantic search:")
            print("      python test_search.py")
            print()
            print("   2. Ready for Module 2: Query Routing & Retrieval")
            print()


def main():
    """Main entry point"""
    try:
        # Check configuration
        is_valid, errors = config.validate()
        if not is_valid:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return
        
        # Run pipeline
        pipeline = IngestionPipeline()
        pipeline.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
