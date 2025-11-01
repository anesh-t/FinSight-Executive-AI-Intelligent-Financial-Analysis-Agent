"""
HTML Parser - Extracts structure from 10-K HTML files
"""
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

class HTMLParser:
    """Parses HTML 10-K filings to extract structured content"""
    
    def __init__(self, config):
        self.config = config
        
    def parse_html_file(self, html_path: str) -> Dict[str, Any]:
        """
        Parse HTML file and extract structured content
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Dictionary with parsed structure
        """
        print(f"📄 Parsing HTML file: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract document metadata
        metadata = self._extract_metadata(soup, html_path)
        
        # Find all sections (Items)
        sections = self._extract_sections(soup)
        
        print(f"   ✅ Found {len(sections)} sections")
        
        return {
            "metadata": metadata,
            "sections": sections
        }
    
    def _extract_metadata(self, soup: BeautifulSoup, html_path: str) -> Dict[str, Any]:
        """Extract document metadata from HTML"""
        
        filename = html_path.split('/')[-1].replace('.html', '').replace('.htm', '')
        
        # Try to extract company name and year from filename or HTML
        # Common pattern: company_10k_2019.html
        parts = filename.lower().split('_')
        
        company = "UNKNOWN"
        year = None
        
        if parts:
            company = parts[0].upper()
            
        # Find year in filename
        year_match = re.search(r'(20\d{2})', filename)
        if year_match:
            year = int(year_match.group(1))
        
        # Try to extract from HTML title or headers
        title_tag = soup.find('title')
        if title_tag and not year:
            title_text = title_tag.get_text()
            year_match = re.search(r'(20\d{2})', title_text)
            if year_match:
                year = int(year_match.group(1))
        
        return {
            "company": company,
            "filing_type": "10-K",
            "fiscal_year": year,
            "source_file": filename
        }
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all sections (Items) from HTML"""
        
        sections = []
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'meta', 'link']):
            element.decompose()
        
        # Find all text blocks
        text_elements = soup.find_all(['p', 'div', 'span', 'td', 'tr', 'table'])
        
        current_item = None
        current_section = None
        accumulated_text = []
        accumulated_tables = []
        
        for element in text_elements:
            text = element.get_text(separator=' ', strip=True)
            
            if not text or len(text) < 10:
                continue
            
            # Check if this is an Item header
            item_match = self._is_item_header(text)
            if item_match:
                # Save previous section
                if current_item and accumulated_text:
                    sections.append({
                        "item": current_item,
                        "heading": current_section or current_item,
                        "text": ' '.join(accumulated_text),
                        "tables": accumulated_tables
                    })
                
                # Start new section
                current_item = item_match['item']
                current_section = item_match['heading']
                accumulated_text = []
                accumulated_tables = []
                continue
            
            # Check if this element contains a table
            if element.name == 'table':
                table_data = self._extract_table_simple(element)
                if table_data:
                    accumulated_tables.append(table_data)
                else:
                    # Table was rejected (likely layout), treat as text
                    if current_item and text:
                        accumulated_text.append(text)
            else:
                # Regular text
                if current_item:
                    accumulated_text.append(text)
        
        # Save last section
        if current_item and accumulated_text:
            sections.append({
                "item": current_item,
                "heading": current_section or current_item,
                "text": ' '.join(accumulated_text),
                "tables": accumulated_tables
            })
        
        return sections
    
    def _is_item_header(self, text: str) -> Optional[Dict[str, str]]:
        """Check if text is an Item header"""
        
        # Pattern: "ITEM 1. Business" or "Item 1A. Risk Factors"
        patterns = [
            r'(?:ITEM|Item)\s+(\d+[A-Z]?)\.\s*(.+)',
            r'(?:PART|Part)\s+([IVX]+)\s*[-—]\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text.strip(), re.IGNORECASE)
            if match:
                return {
                    "item": f"Item {match.group(1)}",
                    "heading": match.group(2).strip()
                }
        
        return None
    
    def _extract_table_simple(self, table_element) -> Optional[Dict[str, Any]]:
        """Extract table data from HTML table element"""
        
        rows = table_element.find_all('tr')
        if len(rows) < self.config.MIN_TABLE_ROWS:
            return None
        
        table_data = []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [cell.get_text(strip=True) for cell in cells]
                if any(row_data):  # Not all empty
                    table_data.append(row_data)
        
        if len(table_data) < self.config.MIN_TABLE_ROWS:
            return None
        
        return {
            "rows": table_data,
            "num_rows": len(table_data),
            "num_cols": len(table_data[0]) if table_data else 0
        }
    
    def extract_subsections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract subsections from text based on headers
        
        Args:
            text: Full section text
            
        Returns:
            List of subsections with headings and text
        """
        subsections = []
        
        # Split by common heading patterns
        # Look for bold/capitalized headers
        lines = text.split('\n')
        
        current_heading = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line looks like a heading
            # (short, mostly caps, ends with period or colon)
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
        
        # If no subsections found, return whole text as one section
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
        if text.isupper():
            return True
        
        # Check if title case and short
        words = text.split()
        if len(words) <= 8 and sum(1 for w in words if w[0].isupper()) >= len(words) * 0.7:
            return True
        
        # Check if ends with period or colon
        if text.endswith(('.', ':')):
            return True
        
        return False
