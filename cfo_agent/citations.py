"""
Citations: fetch provenance from citation views
"""
from typing import List, Dict, Optional
from db.pool import db_pool


class CitationFetcher:
    """Fetches data provenance from citation views"""
    
    async def fetch_citations(self, ticker: str, fiscal_year: int, fiscal_quarter: Optional[int] = None) -> Dict:
        """
        Fetch citations for a company and period
        
        Args:
            ticker: Company ticker
            fiscal_year: Fiscal year
            fiscal_quarter: Fiscal quarter (optional)
            
        Returns:
            Dict with 'financial', 'stock', 'macro' citation info
        """
        citations = {
            'financial': None,
            'stock': None,
            'macro': None
        }
        
        # Fetch financial citation
        citations['financial'] = await self._fetch_financial_citation(ticker, fiscal_year, fiscal_quarter)
        
        # Fetch stock citation
        citations['stock'] = await self._fetch_stock_citation(ticker, fiscal_year, fiscal_quarter)
        
        # Fetch macro citation (just get one indicator as example)
        citations['macro'] = await self._fetch_macro_citation(fiscal_year, fiscal_quarter)
        
        return citations
    
    async def _fetch_financial_citation(self, ticker: str, fiscal_year: int, fiscal_quarter: Optional[int]) -> Optional[Dict]:
        """Fetch financial data citation"""
        if fiscal_quarter:
            sql = """
            SELECT ticker, fiscal_year, fiscal_quarter, source_code, source_name, 
                   as_reported, version_ts
            FROM vw_fact_citations
            WHERE ticker = :ticker AND fiscal_year = :fy AND fiscal_quarter = :fq
            LIMIT 1
            """
            params = {'ticker': ticker, 'fy': fiscal_year, 'fq': fiscal_quarter}
        else:
            sql = """
            SELECT ticker, fiscal_year, source_code, source_name, 
                   as_reported, version_ts
            FROM vw_fact_citations
            WHERE ticker = :ticker AND fiscal_year = :fy
            ORDER BY fiscal_quarter DESC
            LIMIT 1
            """
            params = {'ticker': ticker, 'fy': fiscal_year}
        
        try:
            record = await db_pool.execute_one(sql, params)
            return dict(record) if record else None
        except Exception:
            return None
    
    async def _fetch_stock_citation(self, ticker: str, fiscal_year: int, fiscal_quarter: Optional[int]) -> Optional[Dict]:
        """Fetch stock data citation"""
        if fiscal_quarter:
            sql = """
            SELECT ticker, fiscal_year, fiscal_quarter, source_code, source_name, version_ts
            FROM vw_stock_citations
            WHERE ticker = :ticker AND fiscal_year = :fy AND fiscal_quarter = :fq
            LIMIT 1
            """
            params = {'ticker': ticker, 'fy': fiscal_year, 'fq': fiscal_quarter}
        else:
            sql = """
            SELECT ticker, fiscal_year, source_code, source_name, version_ts
            FROM vw_stock_citations
            WHERE ticker = :ticker AND fiscal_year = :fy
            ORDER BY fiscal_quarter DESC
            LIMIT 1
            """
            params = {'ticker': ticker, 'fy': fiscal_year}
        
        try:
            record = await db_pool.execute_one(sql, params)
            return dict(record) if record else None
        except Exception:
            return None
    
    async def _fetch_macro_citation(self, fiscal_year: int, fiscal_quarter: Optional[int]) -> Optional[Dict]:
        """Fetch macro indicator citation (CPI as example)"""
        sql = """
        SELECT indicator_code, source_code, source_name, version_ts
        FROM vw_macro_citations
        WHERE indicator_code = 'CPIAUCSL'
        ORDER BY quarter_end DESC
        LIMIT 1
        """
        
        try:
            record = await db_pool.execute_one(sql, {})
            return dict(record) if record else None
        except Exception:
            return None
    
    def format_citation_line(self, citations: Dict) -> str:
        """
        Format citations into a single provenance line
        
        Returns:
            String like "Sources: ALPHAVANTAGE_FIN (as_reported, 2025-02-10); FRED; YF"
        """
        sources = []
        
        # Financial
        if citations.get('financial'):
            fin = citations['financial']
            source_str = fin['source_code']
            if fin.get('as_reported'):
                source_str += " (as_reported"
                if fin.get('version_ts'):
                    ts = str(fin['version_ts'])[:19]  # Truncate to datetime
                    source_str += f", {ts}"
                source_str += ")"
            sources.append(source_str)
        
        # Stock
        if citations.get('stock'):
            sources.append(citations['stock']['source_code'])
        
        # Macro
        if citations.get('macro'):
            sources.append(citations['macro']['source_code'])
        
        if sources:
            return "Sources: " + "; ".join(sources)
        else:
            return "Sources: Not available"
