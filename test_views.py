"""
Quick test to check your actual view structure
"""
from database import SupabaseConnector

db = SupabaseConnector()

print("=" * 60)
print("TESTING VIEW STRUCTURE")
print("=" * 60)

# Test 1: Check if views exist and get column names
print("\n1. Testing vw_company_summary:")
try:
    result = db.execute_query("SELECT * FROM vw_company_summary LIMIT 1")
    if not result.empty:
        print(f"✅ View exists! Columns: {list(result.columns)}")
        print(f"Sample row:\n{result.iloc[0]}")
    else:
        print("❌ View is empty")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check company names
print("\n2. Testing company names:")
try:
    result = db.execute_query("SELECT DISTINCT company_name FROM vw_company_summary LIMIT 10")
    if not result.empty:
        print(f"✅ Company names found: {result['company_name'].tolist()}")
    else:
        print("❌ No company names found")
except Exception as e:
    # Try alternative column name
    try:
        result = db.execute_query("SELECT DISTINCT company FROM vw_company_summary LIMIT 10")
        if not result.empty:
            print(f"✅ Companies found (using 'company' column): {result['company'].tolist()}")
    except:
        print(f"❌ Error: {e}")

# Test 3: Check fiscal years
print("\n3. Testing fiscal years:")
try:
    result = db.execute_query("SELECT DISTINCT fiscal_year FROM vw_company_summary ORDER BY fiscal_year")
    if not result.empty:
        print(f"✅ Fiscal years: {result['fiscal_year'].tolist()}")
    else:
        print("❌ No fiscal years found")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Simple query
print("\n4. Testing simple query:")
try:
    result = db.execute_query("""
        SELECT company_name, fiscal_year, revenue 
        FROM vw_company_summary 
        WHERE fiscal_year = 2023 
        LIMIT 5
    """)
    if not result.empty:
        print(f"✅ Query successful! Got {len(result)} rows")
        print(result)
    else:
        print("❌ Query returned no data")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
