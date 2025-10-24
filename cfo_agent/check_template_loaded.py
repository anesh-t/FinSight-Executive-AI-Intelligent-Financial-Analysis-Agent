"""Check what's actually loaded in the template"""
import json

with open('catalog/templates.json', 'r') as f:
    templates = json.load(f)['templates']

quarter_snapshot = templates['quarter_snapshot']

print("\n" + "="*100)
print("QUARTER_SNAPSHOT TEMPLATE")
print("="*100)

print(f"\nIntent: {quarter_snapshot['intent']}")
print(f"Surface: {quarter_snapshot['surface']}")
print(f"\nDescription:")
print(f"  {quarter_snapshot['description']}")

print(f"\nSQL Length: {len(quarter_snapshot['sql'])} characters")
print(f"\nSQL (first 500 chars):")
print(f"  {quarter_snapshot['sql'][:500]}...")

print(f"\nSQL (last 200 chars):")
print(f"  ...{quarter_snapshot['sql'][-200:]}")

print(f"\nParams: {quarter_snapshot['params']}")
print(f"Default Params: {quarter_snapshot['default_params']}")

# Check if vw_ratios_quarter is in the SQL
if 'vw_ratios_quarter' in quarter_snapshot['sql']:
    print(f"\n✅ vw_ratios_quarter found in SQL")
else:
    print(f"\n❌ vw_ratios_quarter NOT found in SQL!")

# Check for all ratio columns
ratio_cols = ['r.gross_margin', 'r.roe', 'r.roa', 'r.debt_to_equity', 'r.debt_to_assets', 'r.rnd_to_revenue', 'r.sgna_to_revenue']
print(f"\nRatio columns in SQL:")
for col in ratio_cols:
    if col in quarter_snapshot['sql']:
        print(f"  ✅ {col}")
    else:
        print(f"  ❌ {col} MISSING")
