"""
SQL validation and whitelist enforcement
"""
import re
from typing import List, Tuple, Dict
from .pool import db_pool


# Allowlist of surfaces the agent can query
ALLOWED_SURFACES = {
    'vw_cfo_answers',
    'vw_company_quarter',
    'vw_company_quarter_macro',
    'mv_financials_annual',
    'mv_ratios_annual',
    'mv_financials_ttm',
    'mv_ratios_ttm',
    'vw_growth_quarter',
    'vw_growth_annual',
    'vw_growth_ttm',
    'vw_peer_stats_quarter',
    'vw_peer_stats_annual',
    'vw_macro_sensitivity_rolling',
    'vw_financial_health_quarter',
    'vw_outliers_quarter',
    'vw_fact_citations',
    'vw_stock_citations',
    'vw_macro_citations',
    'vw_latest_company_quarter',
    'dim_company',  # Needed for JOINs to get ticker names
    'vw_data_dictionary',  # Metric definitions
    'fact_financials',  # Raw financial data with expense details (R&D, SG&A, COGS)
    'vw_ratios_quarter',  # Quarterly ratios (all 9 ratios for quarterly data)
    'vw_stock_prices_quarter',  # Quarterly stock prices
    'mv_stock_prices_annual',  # Annual stock prices aggregated
    'vw_macro_quarter',  # Quarterly macro indicators
    'mv_macro_annual',  # Annual macro indicators aggregated
    'mv_macro_sensitivity_annual',  # Annual macro sensitivity (betas) aggregated
    # Combined views (Layer 1, 2, 3)
    'vw_company_complete_quarter',  # Layer 1: Financials + Ratios + Stock (Quarterly)
    'vw_company_macro_context_quarter',  # Layer 2: Layer 1 + Macro (Quarterly)
    'vw_company_full_quarter',  # Layer 3: Layer 2 + Sensitivity (Quarterly)
    'mv_company_complete_annual',  # Layer 1: Financials + Ratios + Stock (Annual)
    'mv_company_macro_context_annual',  # Layer 2: Layer 1 + Macro (Annual)
    'mv_company_full_annual'  # Layer 3: Layer 2 + Sensitivity (Annual)
}

# Allowed parameter names
ALLOWED_PARAMS = {'ticker', 'fy', 'fq', 'limit', 't1', 't2', 'latest'}

# Schema cache (will be loaded from database)
_schema_cache: Dict[str, List[str]] = {}


async def load_schema_cache():
    """Load schema cache from database"""
    global _schema_cache
    
    sql = """
    SELECT surface_name, column_name
    FROM vw_schema_cache
    WHERE surface_name = ANY($1)
    ORDER BY surface_name, column_name
    """
    
    try:
        records = await db_pool.execute_query(
            sql.replace('$1', ':surfaces'),
            {'surfaces': list(ALLOWED_SURFACES)}
        )
        
        for record in records:
            surface = record['surface_name']
            column = record['column_name']
            if surface not in _schema_cache:
                _schema_cache[surface] = []
            _schema_cache[surface].append(column)
    except Exception as e:
        print(f"Warning: Could not load schema cache: {e}")
        # Continue without schema cache (will skip column validation)


def validate_sql(sql: str, params: dict = None) -> Tuple[bool, str]:
    """
    Validate SQL query against safety rules
    
    Returns:
        (is_valid, error_message)
    """
    params = params or {}
    
    # 1. Check for SELECT-only
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT queries are allowed"
    
    # 2. Check for single statement (no semicolons except at end)
    semicolon_count = sql.count(';')
    if semicolon_count > 1 or (semicolon_count == 1 and not sql.strip().endswith(';')):
        return False, "Multiple statements not allowed"
    
    # 3. Check for DDL/DML keywords
    forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE']
    for keyword in forbidden_keywords:
        if re.search(rf'\b{keyword}\b', sql_upper):
            return False, f"Forbidden keyword: {keyword}"
    
    # 4. Check for SELECT *
    if re.search(r'SELECT\s+\*', sql_upper):
        return False, "SELECT * is not allowed; specify columns explicitly"
    
    # 5. Extract surfaces from FROM/JOIN clauses
    surfaces_in_query = extract_surfaces(sql)
    
    # 6. Check surfaces against allowlist
    for surface in surfaces_in_query:
        if surface not in ALLOWED_SURFACES:
            return False, f"Surface '{surface}' is not in the allowlist"
    
    # 7. Check for LIMIT clause
    if 'LIMIT' not in sql_upper:
        return False, "LIMIT clause is required"
    
    # 8. Extract and validate LIMIT value
    limit_match = re.search(r'LIMIT\s+(:limit|\d+)', sql, re.IGNORECASE)
    if limit_match:
        limit_val = limit_match.group(1)
        if limit_val.isdigit() and int(limit_val) > 200:
            return False, "LIMIT must be ≤ 200"
        elif limit_val == ':limit' and params.get('limit', 0) > 200:
            return False, "LIMIT parameter must be ≤ 200"
    
    # 9. Validate parameters
    for param_name in params.keys():
        if param_name not in ALLOWED_PARAMS:
            return False, f"Parameter '{param_name}' is not allowed"
    
    # 10. Check for cross joins without ON
    if re.search(r'CROSS\s+JOIN', sql_upper):
        return False, "CROSS JOIN is not allowed"
    
    # Check for implicit cross joins (comma-separated tables without WHERE/USING/ON)
    if ',' in sql and 'WHERE' not in sql_upper and 'USING' not in sql_upper and 'ON' not in sql_upper:
        # This is a heuristic; may need refinement
        return False, "Implicit cross join detected; use explicit JOINs with ON clauses"
    
    # 11. Validate columns against schema cache (if loaded)
    # Disabled for now - too strict for JOIN queries
    # if _schema_cache:
    #     column_validation = validate_columns(sql, surfaces_in_query)
    #     if not column_validation[0]:
    #         return column_validation
    
    return True, ""


def extract_surfaces(sql: str) -> List[str]:
    """Extract table/view names from FROM and JOIN clauses"""
    surfaces = []
    
    # Pattern to match FROM/JOIN table_name [AS alias]
    pattern = r'(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)'
    matches = re.findall(pattern, sql, re.IGNORECASE)
    
    for match in matches:
        surface = match.lower()
        if surface not in ['as', 'on', 'using', 'where', 'group', 'order', 'limit']:
            surfaces.append(surface)
    
    return list(set(surfaces))


def validate_columns(sql: str, surfaces: List[str]) -> Tuple[bool, str]:
    """
    Validate that all selected columns exist in the schema cache
    
    This is a simplified validation; a full parser would be more robust
    """
    # Extract column references (simplified)
    # Look for patterns like: SELECT a.col1, b.col2, col3
    
    # For now, we'll do a basic check:
    # If a surface is used, ensure it's in the schema cache
    for surface in surfaces:
        if surface not in _schema_cache:
            return False, f"Surface '{surface}' not found in schema cache"
    
    # TODO: Implement full column validation
    # This would require parsing the SELECT clause and checking each column
    # against the schema cache for the corresponding surface
    
    return True, ""


def get_allowed_surfaces() -> List[str]:
    """Get list of allowed surfaces"""
    return sorted(list(ALLOWED_SURFACES))


def get_schema_for_surface(surface: str) -> List[str]:
    """Get column list for a surface"""
    return _schema_cache.get(surface, [])
