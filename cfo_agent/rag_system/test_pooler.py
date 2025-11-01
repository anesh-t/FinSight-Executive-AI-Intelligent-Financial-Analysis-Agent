"""Test Supabase connection pooler"""
import psycopg2

# Supabase often provides pooler access via different methods
# Let's try the most common ones

configs = [
    {
        'name': 'Session Mode Pooler (6543)',
        'host': 'db.ikhrfgywojsrvxgdojxd.supabase.co',
        'port': 6543,
        'options': '-c statement_timeout=60000'
    },
    {
        'name': 'Transaction Mode Pooler (5432 with mode)',
        'host': 'db.ikhrfgywojsrvxgdojxd.supabase.co',
        'port': 5432,
        'options': '-c pool_mode=transaction'
    },
    {
        'name': 'AWS Pooler (alternative host)',
        'host': 'aws-0-us-east-1.pooler.supabase.com',
        'port': 6543,
        'options': ''
    }
]

password = 'asntrbdrhbcsdgjkt'

print("=" * 80)
print("TESTING SUPABASE POOLER CONNECTIONS")
print("=" * 80)
print()

for config in configs:
    print(f"Testing: {config['name']}")
    print(f"  Host: {config['host']}:{config['port']}")
    
    try:
        conn_string = f"postgresql://postgres:{password}@{config['host']}:{config['port']}/postgres"
        if config['options']:
            conn_string += f"?options={config['options']}"
        
        conn = psycopg2.connect(conn_string, connect_timeout=5)
        
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM document_chunks;')
        count = cursor.fetchone()[0]
        
        print(f"  ✅ SUCCESS!")
        print(f"  Document chunks: {count:,}")
        print(f"  Connection string: {conn_string.replace(password, '***')}")
        print()
        
        # Save successful config
        with open('successful_connection.txt', 'w') as f:
            f.write(f"host={config['host']}\n")
            f.write(f"port={config['port']}\n")
            f.write(f"options={config['options']}\n")
        
        cursor.close()
        conn.close()
        break
        
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:150]}")
        print()

print("=" * 80)
print("If all failed, please:")
print("1. Go to Supabase Dashboard > Project Settings > Database")
print("2. Look for 'Connection Pooling' or 'Pooler' section")
print("3. Copy the 'Session' pooler connection string")
print("=" * 80)
