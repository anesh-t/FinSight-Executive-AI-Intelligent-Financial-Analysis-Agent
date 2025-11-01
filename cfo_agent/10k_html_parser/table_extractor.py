"""
Table Extractor - Properly formats and structures tables from HTML
"""
import re
from typing import Dict, List, Any, Optional

class TableExtractor:
    """Extracts and formats tables from parsed HTML"""
    
    def __init__(self, config):
        self.config = config
        
    def process_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and format tables
        
        Args:
            tables: List of raw table data
            
        Returns:
            List of formatted tables
        """
        formatted_tables = []
        filtered_count = 0
        
        for table in tables:
            formatted = self._format_table(table)
            if formatted:
                formatted_tables.append(formatted)
            else:
                filtered_count += 1
        
        if filtered_count > 0:
            print(f"   🔍 Filtered out {filtered_count} layout tables (keeping {len(formatted_tables)} real data tables)")
        
        return formatted_tables
    
    def _format_table(self, table: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format a single table"""
        
        rows = table.get('rows', [])
        
        if not rows or len(rows) < self.config.MIN_TABLE_ROWS:
            return None
        
        # SMART CHECK: Is this a real data table or just layout?
        if not self._is_real_data_table(rows):
            return None  # Skip layout tables
        
        # Identify header row (usually first row)
        header = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # Clean cells
        header = [self._clean_cell(cell) for cell in header]
        data_rows = [[self._clean_cell(cell) for cell in row] for row in data_rows]
        
        # Create structured format
        formatted = {
            "type": "table",
            "header": header,
            "rows": data_rows,
            "num_rows": len(data_rows),
            "num_cols": len(header),
            "formatted_text": self._table_to_text(header, data_rows)
        }
        
        return formatted
    
    def _is_real_data_table(self, rows: List[List[str]]) -> bool:
        """
        Determine if this is a real data table or just layout HTML
        
        Real data tables have:
        - Multiple numeric values
        - Consistent column structure
        - Short cell values
        - Headers that are descriptive
        """
        if len(rows) < 3:  # Real tables usually have header + multiple data rows
            return False
        
        # Count total cells and numeric cells
        total_cells = 0
        numeric_cells = 0
        long_text_cells = 0
        empty_cells = 0
        
        for row in rows:
            for cell in row:
                total_cells += 1
                cell_clean = cell.strip()
                
                if not cell_clean:
                    empty_cells += 1
                    continue
                
                # Check if cell is numeric (with optional $ % , symbols)
                # Pattern: numbers, dollar signs, percentages, commas, parentheses
                numeric_pattern = re.match(r'^[\$\(]?[\d,]+\.?\d*[\)]?[\%]?$', cell_clean.replace(' ', ''))
                if numeric_pattern or cell_clean.replace(',', '').replace('.', '').replace('$', '').replace('%', '').replace('(', '').replace(')', '').isdigit():
                    numeric_cells += 1
                
                # Check if cell has long text (likely narrative, not table data)
                if len(cell_clean.split()) > 15:
                    long_text_cells += 1
        
        if total_cells == 0:
            return False
        
        # Calculate ratios
        numeric_ratio = numeric_cells / total_cells
        empty_ratio = empty_cells / total_cells
        long_text_ratio = long_text_cells / total_cells
        
        # Real data tables have:
        # - At least 20% numeric values
        # - Less than 50% empty cells
        # - Less than 30% long text cells
        is_data_table = (
            numeric_ratio >= 0.20 and
            empty_ratio < 0.5 and
            long_text_ratio < 0.3 and
            len(rows) >= 3
        )
        
        # Additional check: consistent column count
        col_counts = [len(row) for row in rows]
        if len(set(col_counts)) > 2:  # More than 2 different column counts = inconsistent
            is_data_table = False
        
        return is_data_table
    
    def _clean_cell(self, cell: str) -> str:
        """Clean table cell content"""
        
        # Remove excessive whitespace
        cell = ' '.join(cell.split())
        
        # Remove special characters
        cell = cell.replace('\xa0', ' ')
        cell = cell.replace('\u200b', '')
        
        # Trim length
        if len(cell) > self.config.MAX_CELL_LENGTH:
            cell = cell[:self.config.MAX_CELL_LENGTH] + '...'
        
        return cell.strip()
    
    def _table_to_text(self, header: List[str], rows: List[List[str]]) -> str:
        """Convert table to readable text format"""
        
        lines = []
        
        # Add header
        if header and any(header):
            lines.append(' | '.join(header))
            lines.append('-' * 50)
        
        # Add rows
        for row in rows:
            if any(row):  # Not all empty
                lines.append(' | '.join(row))
        
        return '\n'.join(lines)
    
    def should_extract_as_table(self, text: str) -> bool:
        """Determine if text should be treated as table data"""
        
        # Count numeric patterns
        numbers = len(re.findall(r'\d+', text))
        words = len(text.split())
        
        # High ratio of numbers to words suggests table
        if words > 0 and (numbers / words) > 0.4:
            return True
        
        # Check for multiple columns (tabs or multiple spaces)
        if '\t' in text or '  ' in text:
            return True
        
        return False
    
    def extract_table_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract table structure from plain text"""
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        if len(lines) < self.config.MIN_TABLE_ROWS:
            return None
        
        # Try to parse as table
        rows = []
        for line in lines:
            # Split by multiple spaces or tabs
            cells = re.split(r'\s{2,}|\t+', line)
            cells = [c.strip() for c in cells if c.strip()]
            
            if len(cells) >= self.config.MIN_TABLE_COLS:
                rows.append(cells)
        
        if len(rows) >= self.config.MIN_TABLE_ROWS:
            return {
                "type": "table",
                "rows": rows,
                "num_rows": len(rows),
                "num_cols": len(rows[0]) if rows else 0
            }
        
        return None
