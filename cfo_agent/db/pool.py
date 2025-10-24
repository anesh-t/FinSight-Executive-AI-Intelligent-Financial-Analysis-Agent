"""
Async PostgreSQL connection pool for read-only database access
"""
import os
import asyncpg
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class DatabasePool:
    """Async connection pool manager for Supabase/Postgres"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.db_url = os.getenv('SUPABASE_DB_URL')
        if not self.db_url:
            raise ValueError("SUPABASE_DB_URL environment variable not set")
    
    async def initialize(self, min_size: int = 2, max_size: int = 10):
        """Initialize the connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=5.0,  # 5 second timeout
                server_settings={
                    'application_name': 'cfo_agent',
                    'default_transaction_read_only': 'on'  # Read-only mode
                }
            )
    
    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def execute_query(self, sql: str, params: dict = None, timeout: float = 5.0):
        """
        Execute a SELECT query and return results
        
        Args:
            sql: SQL query string with :param placeholders
            params: Dictionary of parameter values
            timeout: Query timeout in seconds
            
        Returns:
            List of Record objects
        """
        if not self.pool:
            await self.initialize()
        
        # Convert named params to positional
        positional_sql, positional_params = self._convert_params(sql, params or {})
        
        async with self.pool.acquire() as conn:
            try:
                records = await conn.fetch(positional_sql, *positional_params, timeout=timeout)
                return records
            except asyncpg.exceptions.QueryCanceledError:
                raise TimeoutError(f"Query exceeded {timeout}s timeout")
            except Exception as e:
                raise RuntimeError(f"Query execution failed: {str(e)}")
    
    async def execute_one(self, sql: str, params: dict = None, timeout: float = 5.0):
        """Execute a query and return a single row"""
        if not self.pool:
            await self.initialize()
        
        positional_sql, positional_params = self._convert_params(sql, params or {})
        
        async with self.pool.acquire() as conn:
            try:
                record = await conn.fetchrow(positional_sql, *positional_params, timeout=timeout)
                return record
            except asyncpg.exceptions.QueryCanceledError:
                raise TimeoutError(f"Query exceeded {timeout}s timeout")
            except Exception as e:
                raise RuntimeError(f"Query execution failed: {str(e)}")
    
    def _convert_params(self, sql: str, params: dict):
        """Convert :named params to $1, $2, etc."""
        positional_sql = sql
        positional_params = []
        param_index = 1
        
        for key, value in params.items():
            placeholder = f":{key}"
            if placeholder in positional_sql:
                positional_sql = positional_sql.replace(placeholder, f"${param_index}")
                positional_params.append(value)
                param_index += 1
        
        return positional_sql, positional_params


# Global pool instance
db_pool = DatabasePool()
