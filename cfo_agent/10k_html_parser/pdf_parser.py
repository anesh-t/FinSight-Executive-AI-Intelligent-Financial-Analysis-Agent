"""
PDF Parser - Extracts structure from 10-K PDF files
"""
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'pypdf2'
    except ImportError:
        PDF_LIBRARY = None

class PDFParser:
    """Parses PDF 10-K filings to extract structured content"""
    
    def __init__(self, config):
        self.config = config
        if PDF_LIBRARY is None:
            raise ImportError("Please install pdfplumber or PyPDF2: pip install pdfplumber")
        
    def parse_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse PDF file and extract structured content
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with parsed structure
        """
        print(f"📄 Parsing PDF file: {pdf_path}")
        
        # Extract text from PDF
        text, tables = self._extract_from_pdf(pdf_path)
        
        # Extract metadata
        metadata = self._extract_metadata(pdf_path, text)
        
        # Find all sections (Items)
        sections = self._extract_sections(text, tables)
        
        print(f"   ✅ Found {len(sections)} sections")
        
        return {
            "metadata": metadata,
            "sections": sections
        }
    
    def _extract_from_pdf(self, pdf_path: str) -> tuple:
        """Extract text and tables from PDF"""
        
        if PDF_LIBRARY == 'pdfplumber':
            return self._extract_with_pdfplumber(pdf_path)
        else:
            return self._extract_with_pypdf2(pdf_path), []
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> tuple:
        """Extract using pdfplumber (preferred - better table support)"""
        
        all_text = []
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"   📖 Reading {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                if text:
                    all_text.append(text)
                
                # Extract tables with more aggressive settings
                table_settings = {
                    "vertical_strategy": "lines_strict",
                    "horizontal_strategy": "lines_strict",
                    "intersection_tolerance": 3,
                }
                
                try:
                    tables = page.extract_tables(table_settings)
                    if tables:
                        for table in tables:
                            if table and len(table) >= self.config.MIN_TABLE_ROWS:
                                # Filter out tables with all None/empty values
                                valid_rows = [row for row in table if any(cell and str(cell).strip() for cell in row)]
                                if len(valid_rows) >= self.config.MIN_TABLE_ROWS:
                                    all_tables.append({
                                        'rows': valid_rows,
                                        'page': page_num
                                    })
                except Exception as e:
                    # If strict table detection fails, try with more lenient settings
                    try:
                        tables = page.extract_tables({
                            "vertical_strategy": "text",
                            "horizontal_strategy": "text",
                        })
                        if tables:
                            for table in tables:
                                if table and len(table) >= self.config.MIN_TABLE_ROWS:
                                    valid_rows = [row for row in table if any(cell and str(cell).strip() for cell in row)]
                                    if len(valid_rows) >= self.config.MIN_TABLE_ROWS:
                                        all_tables.append({
                                            'rows': valid_rows,
                                            'page': page_num
                                        })
                    except:
                        pass  # Skip tables that can't be extracted
        
        full_text = '\n'.join(all_text)
        print(f"   ✅ Extracted {len(full_text)} characters, {len(all_tables)} potential tables")
        
        return full_text, all_tables
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract using PyPDF2 (fallback - no table support)"""
        
        all_text = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"   📖 Reading {len(reader.pages)} pages...")
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)
        
        full_text = '\n'.join(all_text)
        print(f"   ✅ Extracted {len(full_text)} characters")
        
        return full_text
    
    def _extract_metadata(self, pdf_path: str, text: str) -> Dict[str, Any]:
        """Extract document metadata"""
        
        filename = Path(pdf_path).stem
        
        # Extract company and year from filename or text
        parts = filename.lower().split()
        
        company = "UNKNOWN"
        year = None
        
        # Try to find company name
        if parts:
            company = parts[0].upper()
        
        # Find year in filename
        year_match = re.search(r'(20\d{2})', filename)
        if year_match:
            year = int(year_match.group(1))
        
        # Try to extract from text if not in filename
        if not year:
            year_match = re.search(r'fiscal year (20\d{2})', text[:5000], re.IGNORECASE)
            if year_match:
                year = int(year_match.group(1))
        
        return {
            "company": company,
            "filing_type": "10-K",
            "fiscal_year": year,
            "source_file": filename
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text from PDF artifacts"""
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove timestamps (e.g., "10/25/25, 4:27 PM")
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+[AP]M', '', text)
        
        # Remove "Document" standalone
        text = re.sub(r'\bDocument\b', '', text)
        
        # Remove "Table of Contents" repeated
        text = re.sub(r'Table of Contents\s+Table of Contents', 'Table of Contents', text)
        
        # Remove page numbers like "15/75"
        text = re.sub(r'\d+/\d+', '', text)
        
        # Remove standalone numbers at line start (page numbers)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _extract_sections(self, text: str, tables: List[Dict]) -> List[Dict[str, Any]]:
        """Extract all sections (Items) from text"""
        
        sections = []
        
        # Clean text first
        text = self._clean_text(text)
        
        # Split text by Item headers
        # Pattern: "ITEM 1." or "Item 1A."
        item_pattern = r'(?:ITEM|Item)\s+(\d+[A-Z]?)\.\s*([^\n]+)'
        
        matches = list(re.finditer(item_pattern, text, re.MULTILINE))
        
        if not matches:
            print("   ⚠️  No Item headers found, treating as single section")
            return [{
                "item": "Full Document",
                "heading": "Full Document",
                "text": self._clean_text(text),
                "tables": tables
            }]
        
        for i, match in enumerate(matches):
            item_num = match.group(1)
            item_heading = match.group(2).strip()
            
            # Get text from this Item to next Item (or end)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start_pos:end_pos].strip()
            section_text = self._clean_text(section_text)
            
            # Filter out very short sections (likely parsing errors)
            if len(section_text.split()) < self.config.MIN_SECTION_WORDS:
                continue
            
            sections.append({
                "item": f"Item {item_num}",
                "heading": item_heading,
                "text": section_text,
                "tables": []  # Tables will be associated later
            })
        
        # Associate tables with sections (simplified - by position)
        if tables:
            sections[0]['tables'] = tables  # For now, add all tables to first section
        
        return sections
    
    def extract_subsections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract subsections from text based on headers
        
        Args:
            text: Full section text
            
        Returns:
            List of subsections with headings and text
        """
        subsections = []
        
        # Split by lines
        lines = text.split('\n')
        
        current_heading = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line looks like a heading
            if self._looks_like_heading(line):
                # Save previous subsection
                if current_heading and current_text:
                    subsections.append({
                        "subheading": current_heading,
                        "text": ' '.join(current_text)
                    })
                
                current_heading = line
                current_text = []
            else:
                current_text.append(line)
        
        # Save last subsection
        if current_heading and current_text:
            subsections.append({
                "subheading": current_heading,
                "text": ' '.join(current_text)
            })
        
        # If no subsections found, return whole text
        if not subsections:
            subsections.append({
                "subheading": None,
                "text": text
            })
        
        return subsections
    
    def _looks_like_heading(self, text: str) -> bool:
        """Determine if text looks like a heading"""
        
        if len(text) > 100:
            return False
        
        # Check if mostly uppercase
        if text.isupper() and len(text.split()) <= 10:
            return True
        
        # Check if title case and short
        words = text.split()
        if len(words) <= 8 and sum(1 for w in words if w and w[0].isupper()) >= len(words) * 0.7:
            return True
        
        return False
