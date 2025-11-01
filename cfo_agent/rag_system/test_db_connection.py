"""Test database connection with different methods"""
import psycopg2

connection_configs = [
    {
        'name': 'Direct connection (port 5432)',
        'host': 'db.ikhrfgywojsrvxgdojxd.supabase.co',
        'port': 5432
    },
    {
        'name': 'Transaction pooler (port 6543)',
        'host': 'db.ikhrfgywojsrvxgdojxd.supabase.co',
        'port': 6543
    }
]

password = 'asntrbdrhbcsdgjkt'

print("=" * 80)
print("TESTING DATABASE CONNECTIONS")
print("=" * 80)
print()

success = False

for config in connection_configs:
    print(f"Trying: {config['name']}")
    print(f"  Host: {config['host']}:{config['port']}")
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database='postgres',
            user='postgres',
            password=password,
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM document_chunks;')
        count = cursor.fetchone()[0]
        
        print(f"  ✅ SUCCESS!")
        print(f"  Document chunks: {count:,}")
        print()
        
        cursor.close()
        conn.close()
        success = True
        break
        
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:100]}")
        print()

if not success:
    print("=" * 80)
    print("ALL CONNECTION ATTEMPTS FAILED")
    print("=" * 80)
    print()
    print("This might be a DNS issue. Let's try using the Supabase API URL instead.")
    print("Check if you can access: https://ikhrfgywojsrvxgdojxd.supabase.co")
