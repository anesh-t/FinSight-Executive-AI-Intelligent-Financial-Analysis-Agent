"""
JSON Processor - Extract chunks from 10-K JSON files
Processes validated JSON files and extracts structured chunks with metadata.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config


@dataclass
class ChunkData:
    """Structured representation of a single chunk"""
    # Document metadata
    company: str                    # e.g., "2024AMZN_10K"
    company_name: str               # e.g., "Amazon"
    ticker: Optional[str]           # e.g., "AMZN"
    fiscal_year: int                # e.g., 2024
    source_file: str                # Original filename
    
    # Section information
    section: str                    # e.g., "Item 1A"
    section_type: str               # e.g., "Risk Factors"
    heading: str                    # Main heading
    subheading: Optional[str]       # AI-generated subheading
    
    # Content
    chunk_text: str                 # Full text content
    word_count: int                 # Number of words
    
    # Positioning
    chunk_index: Optional[int]      # Position in section
    chunk_total: Optional[int]      # Total chunks in section
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database insertion"""
        return {
            'company': self.company,
            'company_name': self.company_name,
            'ticker': self.ticker,
            'fiscal_year': self.fiscal_year,
            'source_file': self.source_file,
            'section': self.section,
            'section_type': self.section_type,
            'heading': self.heading,
            'subheading': self.subheading,
            'chunk_text': self.chunk_text,
            'word_count': self.word_count,
            'chunk_index': self.chunk_index,
            'chunk_total': self.chunk_total
        }


class CompanyMapper:
    """Maps company identifiers to normalized names and tickers"""
    
    COMPANY_MAP = {
        'AMZN': {'name': 'Amazon', 'ticker': 'AMZN', 'aliases': ['amazon', 'amzn']},
        'AAPL': {'name': 'Apple', 'ticker': 'AAPL', 'aliases': ['apple', 'aapl']},
        'GOOGL': {'name': 'Google', 'ticker': 'GOOGL', 'aliases': ['google', 'alphabet', 'goog', 'googl']},
        'META': {'name': 'Meta', 'ticker': 'META', 'aliases': ['meta', 'facebook', 'fb']},
        'MSFT': {'name': 'Microsoft', 'ticker': 'MSFT', 'aliases': ['microsoft', 'msft']}
    }
    
    @classmethod
    def normalize_company(cls, company_str: str) -> tuple[str, Optional[str]]:
        """
        Extract normalized company name and ticker from company string.
        
        Args:
            company_str: e.g., "2024AMZN_10K" or "2024Amazon_10K"
            
        Returns:
            (company_name, ticker) e.g., ("Amazon", "AMZN")
        """
        company_lower = company_str.lower()
        
        for ticker, info in cls.COMPANY_MAP.items():
            # Check if any alias is in the company string
            for alias in info['aliases']:
                if alias in company_lower:
                    return (info['name'], info['ticker'])
        
        # Fallback: return as-is
        return (company_str, None)


class SectionMapper:
    """Maps section codes to human-readable names"""
    
    SECTION_MAP = {
        'Item 1': 'Business',
        'Item 1A': 'Risk Factors',
        'Item 1B': 'Unresolved Staff Comments',
        'Item 2': 'Properties',
        'Item 3': 'Legal Proceedings',
        'Item 4': 'Mine Safety Disclosures',
        'Item 5': 'Market for Registrant Common Equity',
        'Item 6': 'Selected Financial Data',
        'Item 7': 'MD&A',
        'Item 7A': 'Quantitative and Qualitative Disclosures',
        'Item 8': 'Financial Statements',
        'Item 9': 'Changes and Disagreements',
        'Item 9A': 'Controls and Procedures',
        'Item 9B': 'Other Information',
        'Item 10': 'Directors and Officers',
        'Item 11': 'Executive Compensation',
        'Item 12': 'Security Ownership',
        'Item 13': 'Certain Relationships',
        'Item 14': 'Principal Accountant Fees',
        'Item 15': 'Exhibits',
        'Item 16': 'Form 10-K Summary'
    }
    
    @classmethod
    def get_section_type(cls, section_code: str) -> str:
        """Get human-readable section name"""
        return cls.SECTION_MAP.get(section_code, section_code)


class JSONProcessor:
    """Process 10-K JSON files and extract chunks"""
    
    def __init__(self, json_folder: Path):
        self.json_folder = Path(json_folder)
        self.stats = {
            'files_processed': 0,
            'chunks_extracted': 0,
            'errors': []
        }
    
    def process_single_file(self, filepath: Path) -> List[ChunkData]:
        """
        Process a single JSON file and extract all chunks.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of ChunkData objects
        """
        chunks = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract document metadata
            metadata = data.get('document_metadata', {})
            company_raw = metadata.get('company', '')
            company_name, ticker = CompanyMapper.normalize_company(company_raw)
            fiscal_year = metadata.get('fiscal_year', 0)
            source_file = metadata.get('source_file', filepath.stem)
            
            # Process each section (item)
            items = data.get('items', {})
            for section_code, section_data in items.items():
                heading = section_data.get('heading', '')
                section_type = SectionMapper.get_section_type(section_code)
                
                # Process each chunk in the section
                content_list = section_data.get('content', [])
                for chunk_dict in content_list:
                    chunk = ChunkData(
                        company=company_raw,
                        company_name=company_name,
                        ticker=ticker,
                        fiscal_year=fiscal_year,
                        source_file=source_file,
                        section=section_code,
                        section_type=section_type,
                        heading=heading,
                        subheading=chunk_dict.get('subheading'),
                        chunk_text=chunk_dict.get('text', ''),
                        word_count=chunk_dict.get('word_count', 0),
                        chunk_index=chunk_dict.get('chunk_info', {}).get('index'),
                        chunk_total=chunk_dict.get('chunk_info', {}).get('total')
                    )
                    chunks.append(chunk)
            
            self.stats['files_processed'] += 1
            self.stats['chunks_extracted'] += len(chunks)
            
        except Exception as e:
            error_msg = f"Error processing {filepath.name}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return chunks
    
    def process_all_files(self) -> List[ChunkData]:
        """
        Process all JSON files in the folder.
        
        Returns:
            List of all ChunkData objects from all files
        """
        all_chunks = []
        
        # Get all JSON files
        json_files = sorted(self.json_folder.glob('*.json'))
        
        if not json_files:
            print(f"⚠️  No JSON files found in {self.json_folder}")
            return []
        
        print(f"📁 Found {len(json_files)} JSON files")
        print(f"📂 Processing files from: {self.json_folder}")
        print()
        
        # Process each file
        for filepath in json_files:
            print(f"  Processing: {filepath.name}...", end=' ')
            chunks = self.process_single_file(filepath)
            all_chunks.extend(chunks)
            print(f"✅ {len(chunks)} chunks")
        
        return all_chunks
    
    def print_stats(self):
        """Print processing statistics"""
        print()
        print("=" * 70)
        print("JSON PROCESSING STATISTICS")
        print("=" * 70)
        print(f"Files Processed:    {self.stats['files_processed']}")
        print(f"Chunks Extracted:   {self.stats['chunks_extracted']}")
        print(f"Errors:             {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\nErrors:")
            for error in self.stats['errors']:
                print(f"  - {error}")
        print("=" * 70)


def main():
    """Test the JSON processor"""
    print("Testing JSON Processor...")
    print()
    
    # Initialize processor
    processor = JSONProcessor(config.paths.json_folder)
    
    # Process all files
    chunks = processor.process_all_files()
    
    # Print statistics
    processor.print_stats()
    
    # Show sample chunk
    if chunks:
        print("\nSample Chunk:")
        print("-" * 70)
        sample = chunks[0]
        print(f"Company: {sample.company_name} ({sample.ticker})")
        print(f"Year: {sample.fiscal_year}")
        print(f"Section: {sample.section} - {sample.section_type}")
        print(f"Heading: {sample.heading}")
        print(f"Subheading: {sample.subheading}")
        print(f"Words: {sample.word_count}")
        print(f"Text preview: {sample.chunk_text[:200]}...")
        print("-" * 70)
    
    return chunks


if __name__ == "__main__":
    main()
