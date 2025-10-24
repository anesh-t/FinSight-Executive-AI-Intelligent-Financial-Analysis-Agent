"""
Entity resolution: map company names/aliases to tickers
"""
from typing import Optional, Dict
from .pool import db_pool


# Cache for ticker resolution
_ticker_cache: Dict[str, str] = {}


async def load_ticker_cache():
    """Load company ticker mappings from database"""
    global _ticker_cache
    
    sql = """
    SELECT ticker, name, aliases
    FROM dim_company
    ORDER BY ticker
    """
    
    try:
        records = await db_pool.execute_query(sql, {})
        
        for record in records:
            ticker = record['ticker']
            name = record['name']
            aliases = record.get('aliases') or []
            
            # Map ticker to itself
            _ticker_cache[ticker.upper()] = ticker
            
            # Map name to ticker
            _ticker_cache[name.upper()] = ticker
            
            # Map aliases to ticker
            for alias in aliases:
                _ticker_cache[alias.upper()] = ticker
        
        print(f"Loaded {len(_ticker_cache)} ticker mappings")
    except Exception as e:
        print(f"Warning: Could not load ticker cache: {e}")


async def resolve_ticker(entity: str) -> Optional[str]:
    """
    Resolve a company name or alias to a ticker
    
    Args:
        entity: Company name, alias, or ticker
        
    Returns:
        Ticker symbol or None if not found
    """
    if not _ticker_cache:
        await load_ticker_cache()
    
    # Try exact match first
    entity_upper = entity.upper().strip()
    if entity_upper in _ticker_cache:
        return _ticker_cache[entity_upper]
    
    # Try fuzzy match (remove common suffixes)
    entity_clean = entity_upper.replace(' INC', '').replace(' CORP', '').replace(' LTD', '').strip()
    if entity_clean in _ticker_cache:
        return _ticker_cache[entity_clean]
    
    # Not found
    return None


async def resolve_entities(entities: list) -> Dict[str, str]:
    """
    Resolve multiple entities to tickers
    
    Returns:
        Dict mapping original entity to ticker (or None if not found)
    """
    results = {}
    for entity in entities:
        ticker = await resolve_ticker(entity)
        results[entity] = ticker
    return results


async def get_latest_period(ticker: str) -> Optional[Dict]:
    """
    Get the latest fiscal year and quarter for a company
    
    Returns:
        Dict with 'fiscal_year' and 'fiscal_quarter' or None
    """
    sql = """
    SELECT lq.fiscal_year, lq.fiscal_quarter
    FROM vw_latest_company_quarter lq
    JOIN dim_company c ON c.company_id = lq.company_id
    WHERE c.ticker = :ticker
    LIMIT 1
    """
    
    try:
        record = await db_pool.execute_one(sql, {'ticker': ticker})
        if record:
            return {
                'fiscal_year': record['fiscal_year'],
                'fiscal_quarter': record['fiscal_quarter']
            }
    except Exception as e:
        print(f"Error getting latest period for {ticker}: {e}")
    
    return None
