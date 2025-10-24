"""
SQL execution with read-only access and timeout
"""
from typing import List, Dict, Tuple
from db.pool import db_pool


class SQLExecutor:
    """Executes validated SQL queries against the database"""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
    
    async def execute(self, sql: str, params: Dict) -> List[Dict]:
        """
        Execute SQL query and return results as list of dicts
        
        Args:
            sql: Validated SQL query
            params: Query parameters
            
        Returns:
            List of result rows as dicts
        """
        try:
            records = await db_pool.execute_query(sql, params, timeout=self.timeout)
            
            # Convert asyncpg Records to dicts
            results = [dict(record) for record in records]
            
            return results
        except TimeoutError as e:
            raise TimeoutError(f"Query exceeded {self.timeout}s timeout")
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {str(e)}")
    
    async def dry_run(self, sql: str, params: Dict) -> bool:
        """
        Dry-run query with LIMIT 1 to test validity
        
        Returns:
            True if query executes successfully
        """
        # Modify SQL to add LIMIT 1 if not present
        dry_run_sql = sql
        if 'LIMIT' not in sql.upper():
            dry_run_sql = sql.rstrip(';').rstrip() + ' LIMIT 1'
        else:
            # Replace existing LIMIT with LIMIT 1
            import re
            dry_run_sql = re.sub(r'LIMIT\s+\d+', 'LIMIT 1', sql, flags=re.IGNORECASE)
        
        try:
            await db_pool.execute_query(dry_run_sql, params, timeout=2.0)
            return True
        except Exception:
            return False
    
    async def execute_with_fallback(self, sql_candidates: List[Tuple[str, Dict]]) -> Tuple[List[Dict], str, Dict]:
        """
        Execute SQL candidates in order, return first successful result
        
        Args:
            sql_candidates: List of (sql, params) tuples
            
        Returns:
            (results, sql_used, params_used)
        """
        for sql, params in sql_candidates:
            try:
                results = await self.execute(sql, params)
                return results, sql, params
            except Exception as e:
                continue
        
        raise RuntimeError("All SQL candidates failed execution")
