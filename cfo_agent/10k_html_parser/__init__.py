"""
10-K HTML Parser Pipeline

Parses raw HTML 10-K filings and produces clean, structured JSON
with proper headings, subheadings, tables, and chunked text.
"""

from .config import HTMLParserConfig
from .html_parser import HTMLParser
from .table_extractor import TableExtractor
from .text_rewriter import TextRewriter
from .text_chunker import TextChunker
from .pipeline import HTMLToJSONPipeline

__version__ = "1.0.0"
__all__ = [
    "HTMLParserConfig",
    "HTMLParser",
    "TableExtractor",
    "TextRewriter",
    "TextChunker",
    "HTMLToJSONPipeline"
]
