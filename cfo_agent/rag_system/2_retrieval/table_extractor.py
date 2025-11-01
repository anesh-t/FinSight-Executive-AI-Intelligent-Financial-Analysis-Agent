"""
Table Extractor - Extract and format tables from 10-K text
Detects tables in unstructured text and formats them for display
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ExtractedTable:
    """Represents an extracted table"""
    title: str
    headers: List[str]
    rows: List[List[str]]
    source_text: str
    table_type: str  # 'financial', 'percentage', 'general'
    
    def to_markdown(self) -> str:
        """Convert table to markdown format"""
        if not self.headers or not self.rows:
            return ""
        
        # Build markdown table
        lines = []
        
        # Title
        if self.title:
            lines.append(f"**{self.title}**\n")
        
        # Headers
        header_line = "| " + " | ".join(self.headers) + " |"
        separator = "|" + "|".join(["---" for _ in self.headers]) + "|"
        lines.append(header_line)
        lines.append(separator)
        
        # Rows
        for row in self.rows:
            row_line = "| " + " | ".join(row) + " |"
            lines.append(row_line)
        
        return "\n".join(lines)
    
    def to_formatted_text(self) -> str:
        """Convert table to formatted text for LLM"""
        if not self.headers or not self.rows:
            return ""
        
        lines = []
        
        # Title
        if self.title:
            lines.append(f"\n{self.title}")
            lines.append("─" * 60)
        
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(self.headers):
            max_width = len(header)
            for row in self.rows:
                if i < len(row):
                    max_width = max(max_width, len(row[i]))
            col_widths.append(min(max_width, 25))  # Cap at 25 chars
        
        # Headers
        header_line = "  ".join(
            header.ljust(col_widths[i])
            for i, header in enumerate(self.headers)
        )
        lines.append(header_line)
        lines.append("─" * len(header_line))
        
        # Rows
        for row in self.rows:
            row_line = "  ".join(
                (row[i] if i < len(row) else "").ljust(col_widths[i])
                for i in range(len(self.headers))
            )
            lines.append(row_line)
        
        return "\n".join(lines)


class TableExtractor:
    """Extract tables from unstructured 10-K text"""
    
    # Patterns that indicate table presence
    TABLE_INDICATORS = [
        r'\d{4}\s+\d{4}\s+\d{4}',  # Years: 2019 2018 2017
        r'\$\s*[\d,]+',  # Dollar amounts: $ 123,456
        r'\d+\.\d+%',  # Percentages: 12.3%
        r'^\s*\w+\s+\$',  # Row label followed by $
    ]
    
    def detect_tables(self, text: str) -> bool:
        """Check if text contains tables"""
        # Look for multiple table indicators
        indicator_count = sum(
            1 for pattern in self.TABLE_INDICATORS
            if re.search(pattern, text, re.MULTILINE)
        )
        
        # Also check for common financial table headers
        has_financial_headers = any(
            keyword in text.lower()
            for keyword in ['gross margin', 'net sales', 'revenue', 'total assets', 
                          'liabilities', 'cash flow', 'income', 'expenses']
        )
        
        return indicator_count >= 2 or (indicator_count >= 1 and has_financial_headers)
    
    def extract_tables(self, text: str) -> List[ExtractedTable]:
        """Extract all tables from text"""
        if not self.detect_tables(text):
            return []
        
        tables = []
        
        # Try to extract year-based financial tables
        year_table = self._extract_year_based_table(text)
        if year_table:
            tables.append(year_table)
        
        return tables
    
    def _extract_year_based_table(self, text: str) -> Optional[ExtractedTable]:
        """Extract tables with year columns (most common in 10-Ks)"""
        
        # Find year headers (e.g., "2019 2018 2017")
        year_pattern = r'(\d{4})\s+(\d{4})(?:\s+(\d{4}))?'
        year_match = re.search(year_pattern, text)
        
        if not year_match:
            return None
        
        years = [y for y in year_match.groups() if y]
        
        # Find the title (text before years, last 2 lines)
        lines_before = text[:year_match.start()].strip().split('\n')
        title_candidates = [l.strip() for l in lines_before[-2:] if l.strip()]
        title = title_candidates[-1] if title_candidates else "Financial Data"
        # Clean title
        title = re.sub(r'\(.*?\)', '', title).strip()
        if len(title) > 100:
            title = "Financial Data"
        
        # Extract table section (from year line onwards)
        table_start_line = year_match.start()
        table_end = min(len(text), year_match.end() + 1500)
        table_text = text[table_start_line:table_end]
        
        # Parse rows
        rows = []
        lines = table_text.split('\n')
        
        # Skip the year header line
        start_parsing = False
        for line in lines[1:]:  # Skip first line (years)
            line_stripped = line.strip()
            
            # Skip empty lines and section headers
            if not line_stripped or len(line_stripped) < 3:
                continue
            
            # Check if this looks like a data row (has $ or % or digits)
            has_data = '$' in line or '%' in line or re.search(r'\d{1,3}(,\d{3})*', line)
            
            if has_data:
                # Try to parse the line
                # Remove multiple spaces, tabs
                cleaned = re.sub(r'\s+', ' ', line_stripped)
                
                # Split by spaces to find values
                parts = cleaned.split()
                
                # Find the label (everything before numbers/$ start)
                label_parts = []
                value_parts = []
                found_value = False
                
                for part in parts:
                    if not found_value and not re.search(r'[\d\$%]', part):
                        label_parts.append(part)
                    else:
                        found_value = True
                        # Clean value
                        clean_val = part.replace('$', '').strip()
                        if clean_val:
                            value_parts.append(part)
                
                if label_parts and value_parts:
                    label = ' '.join(label_parts)
                    # Take last N values matching year count
                    values = value_parts[-len(years):] if len(value_parts) >= len(years) else value_parts
                    
                    # Pad if needed
                    while len(values) < len(years):
                        values.insert(0, '')
                    
                    rows.append([label] + values[:len(years)])
            
            # Stop if we hit next major section
            if len(rows) > 20 or (start_parsing and any(
                keyword in line_stripped.lower()
                for keyword in ['products gross margin', 'services gross margin', 'the company', 'apple inc']
            )):
                break
            
            if has_data:
                start_parsing = True
        
        if len(rows) < 2:
            return None
        
        # Detect table type
        table_type = 'financial'
        all_text = ' '.join(' '.join(row) for row in rows)
        if '%' in all_text:
            table_type = 'percentage' if '$' not in all_text else 'financial'
        
        return ExtractedTable(
            title=title,
            headers=['Metric'] + years,
            rows=rows,
            source_text=table_text[:500],
            table_type=table_type
        )
    
    def extract_and_format(self, text: str, format_type: str = 'markdown') -> str:
        """
        Extract tables and return formatted string
        
        Args:
            text: Source text
            format_type: 'markdown' or 'text'
        """
        tables = self.extract_tables(text)
        
        if not tables:
            return ""
        
        formatted_tables = []
        for table in tables:
            if format_type == 'markdown':
                formatted_tables.append(table.to_markdown())
            else:
                formatted_tables.append(table.to_formatted_text())
        
        return "\n\n".join(formatted_tables)
    
    def has_financial_tables(self, text: str) -> bool:
        """Quick check if text has financial tables"""
        return self.detect_tables(text)


# Convenience functions
def extract_tables_from_text(text: str) -> List[ExtractedTable]:
    """Extract tables from text"""
    extractor = TableExtractor()
    return extractor.extract_tables(text)


def format_tables_for_display(text: str) -> str:
    """Extract and format tables for display"""
    extractor = TableExtractor()
    return extractor.extract_and_format(text, format_type='markdown')


def has_tables(text: str) -> bool:
    """Check if text contains tables"""
    extractor = TableExtractor()
    return extractor.detect_tables(text)


if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Gross Margin
    Products and Services gross margin and gross margin percentage for 2019, 2018 and 2017 were as follows (dollars in millions):
    2019 2018 2017
    Gross margin:
    Products $ 68,887 $ 77,683 $ 70,197
    Services 29,505 24,156 17,989
    Total gross margin $ 98,392 $ 101,839 $ 88,186
    Gross margin percentage:
    Products 32.2% 34.4% 35.7%
    Services 63.7% 60.8% 55.0%
    Total gross margin percentage 37.8% 38.3% 38.5%
    """
    
    extractor = TableExtractor()
    
    print("Testing table extraction...")
    print("=" * 80)
    
    # Check detection
    has_table = extractor.detect_tables(sample_text)
    print(f"Has tables: {has_table}")
    print()
    
    # Extract tables
    tables = extractor.extract_tables(sample_text)
    print(f"Found {len(tables)} table(s)")
    print()
    
    # Display formatted tables
    for i, table in enumerate(tables, 1):
        print(f"Table {i}: {table.title}")
        print(f"Type: {table.table_type}")
        print()
        print("Markdown format:")
        print(table.to_markdown())
        print()
        print("Text format:")
        print(table.to_formatted_text())
        print("=" * 80)
