"""
SQL builder: template-first with guarded generative fallback
"""
from typing import Dict, Tuple, Optional
from db.whitelist import validate_sql
from generative_sql import GenerativeSQLBuilder


class SQLBuilder:
    """Builds and validates SQL queries using templates or generation"""
    
    def __init__(self):
        self.generative_builder = GenerativeSQLBuilder()
    
    async def build_sql(self, plan: Dict, use_generative: bool = False) -> Tuple[str, Dict, bool]:
        """
        Build SQL query from plan
        
        Args:
            plan: Execution plan with 'sql', 'params', 'surfaces'
            use_generative: Force generative SQL path
            
        Returns:
            (sql, params, is_generative)
        """
        if use_generative:
            # Generative path
            return await self._build_generative(plan)
        else:
            # Template path (default)
            return await self._build_from_template(plan)
    
    async def _build_from_template(self, plan: Dict) -> Tuple[str, Dict, bool]:
        """Build SQL from template"""
        sql = plan['sql']
        params = plan['params']
        
        # Validate SQL
        is_valid, error_msg = validate_sql(sql, params)
        
        if not is_valid:
            raise ValueError(f"Template SQL validation failed: {error_msg}")
        
        return sql, params, False
    
    async def _build_generative(self, plan: Dict) -> Tuple[str, Dict, bool]:
        """Build SQL using generative approach"""
        # Extract context from plan
        context = {
            'intent': plan.get('intent'),
            'surfaces': plan.get('surfaces', []),
            'entities_resolved': plan.get('entities_resolved', {}),
            'params': plan.get('params', {})
        }
        
        # Generate SQL candidates
        candidates = await self.generative_builder.generate_sql(context)
        
        # Validate and select best candidate
        for sql, params in candidates:
            is_valid, error_msg = validate_sql(sql, params)
            if is_valid:
                # Try dry-run
                try:
                    # This would be implemented in sql_exec.py
                    # For now, just return the first valid candidate
                    return sql, params, True
                except Exception as e:
                    continue
        
        # All candidates failed
        raise ValueError("All generated SQL candidates failed validation")
    
    def validate_and_fix(self, sql: str, params: Dict) -> Tuple[str, Dict, bool]:
        """
        Validate SQL and attempt automatic fixes
        
        Returns:
            (fixed_sql, params, was_fixed)
        """
        is_valid, error_msg = validate_sql(sql, params)
        
        if is_valid:
            return sql, params, False
        
        # Attempt automatic fixes
        fixed_sql = sql
        was_fixed = False
        
        # Fix 1: Add LIMIT if missing
        if "LIMIT clause is required" in error_msg:
            fixed_sql = sql.rstrip(';').rstrip() + " LIMIT :limit"
            if 'limit' not in params:
                params['limit'] = 25
            was_fixed = True
        
        # Fix 2: Replace SELECT * with explicit columns (would need schema info)
        # This is complex and better handled by regeneration
        
        # Validate fixed SQL
        if was_fixed:
            is_valid, error_msg = validate_sql(fixed_sql, params)
            if is_valid:
                return fixed_sql, params, True
        
        # Could not fix
        raise ValueError(f"SQL validation failed: {error_msg}")
