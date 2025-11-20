"""
Configuration for 10-K HTML Parser Pipeline
"""
import os
from pathlib import Path

class HTMLParserConfig:
    """Configuration settings for HTML parsing pipeline"""
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent
    INPUT_DIR = BASE_DIR / "10k-fillings-pdfs"
    OUTPUT_DIR = BASE_DIR / "parsed_10k_json"
    LOGS_DIR = BASE_DIR / "10k_html_parser" / "logs"
    
    # Text processing thresholds
    MIN_TEXT_LENGTH = 50              # Minimum chars for valid text
    MAX_CHUNK_WORDS = 400             # Split if section exceeds this
    OPTIMAL_CHUNK_SIZE = 300          # Target size for chunks
    MIN_CHUNK_WORDS = 150             # Minimum words per chunk
    CONTEXT_OVERLAP = 50              # Overlap between chunks
    
    # Table parsing
    MIN_TABLE_ROWS = 2                # Minimum rows for valid table
    MIN_TABLE_COLS = 2                # Minimum columns
    MAX_CELL_LENGTH = 500             # Max chars per table cell
    
    # LLM settings (using latest model)
    LLM_MODEL = "gpt-5.1"         # Latest and most capable
    LLM_TEMPERATURE = 0.3
    MAX_RETRIES = 3
    
    # Section detection patterns
    SECTION_PATTERNS = [
        r"^ITEM\s+(\d+[A-Z]?)\.",
        r"^Item\s+(\d+[A-Z]?)\.",
        r"^PART\s+([IVX]+)",
    ]
    
    # Processing settings
    ENABLE_TEXT_REWRITING = True      # Use LLM to fix parsing errors
    ENABLE_AI_SUBHEADINGS = True      # Generate missing subheadings
    ENABLE_TABLE_FORMATTING = True    # Format tables properly
    ENABLE_CHUNKING = True            # Split long texts
    
    # Quality validation
    MIN_SECTION_WORDS = 10
    MAX_SECTION_WORDS = 10000
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
        cls.LOGS_DIR.mkdir(exist_ok=True, parents=True)
        
    @classmethod
    def get_openai_key(cls):
        """Get OpenAI API key from environment"""
        return os.getenv("OPENAI_API_KEY")
