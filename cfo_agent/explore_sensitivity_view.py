"""
Explore the macro sensitivity rolling view structure
"""
import asyncio
from db.pool import db_pool

async def explore_sensitivity():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("EXPLORING MACRO SENSITIVITY VIEW")
    print("="*100)
    
    # Check schema
    print("\n[1] SCHEMA:")
    schema_query = """
        SELECT 
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = 'vw_macro_sensitivity_rolling'
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """
    
    cols = await db_pool.execute_query(schema_query)
    print(f"\n{'Column':<40} {'Type':<20}")
    print("-"*60)
    for col in cols:
        print(f"{col['column_name']:<40} {col['data_type']:<20}")
    
    # Check sample data
    print("\n[2] SAMPLE DATA (2023 Q2):")
    sample_query = """
        SELECT 
            c.ticker,
            s.fiscal_year,
            s.fiscal_quarter,
            ROUND(s.gross_margin::numeric, 4) as gm,
            ROUND(s.operating_margin::numeric, 4) as om,
            ROUND(s.net_margin::numeric, 4) as nm,
            ROUND(s.beta_gm_cpi_12q::numeric, 4) as beta_gm_cpi,
            ROUND(s.beta_om_cpi_12q::numeric, 4) as beta_om_cpi,
            ROUND(s.beta_nm_cpi_12q::numeric, 4) as beta_nm_cpi,
            ROUND(s.beta_nm_spx_12q::numeric, 4) as beta_nm_spx
        FROM vw_macro_sensitivity_rolling s
        JOIN dim_company c USING (company_id)
        WHERE s.fiscal_year = 2023 AND s.fiscal_quarter = 2
        ORDER BY c.ticker
    """
    
    result = await db_pool.execute_query(sample_query)
    for row in result:
        print(f"\n{row['ticker']} Q{row['fiscal_quarter']} {row['fiscal_year']}:")
        print(f"  Margins: GM={row['gm']}, OM={row['om']}, NM={row['nm']}")
        print(f"  Betas (CPI): GM={row['beta_gm_cpi']}, OM={row['beta_om_cpi']}, NM={row['beta_nm_cpi']}")
        print(f"  Beta (S&P): NM={row['beta_nm_spx']}")
    
    # Check data availability
    print("\n[3] DATA AVAILABILITY:")
    avail_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT company_id) as num_companies,
            MIN(fiscal_year) as earliest_year,
            MAX(fiscal_year) as latest_year,
            COUNT(CASE WHEN beta_nm_cpi_12q IS NOT NULL THEN 1 END) as records_with_betas
        FROM vw_macro_sensitivity_rolling
    """
    
    result = await db_pool.execute_query(avail_query)
    r = result[0]
    print(f"  Total Records: {r['total_records']}")
    print(f"  Companies: {r['num_companies']}")
    print(f"  Years: {r['earliest_year']} - {r['latest_year']}")
    print(f"  Records with Betas: {r['records_with_betas']}")
    
    await db_pool.close()
    
    print("\n" + "="*100)

if __name__ == "__main__":
    asyncio.run(explore_sensitivity())
