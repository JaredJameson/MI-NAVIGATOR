import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Check if report_versions table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_versions';")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ report_versions table exists")
    
    # Get schema
    cursor.execute("PRAGMA table_info(report_versions);")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check if there are any versions
    cursor.execute("SELECT COUNT(*) FROM report_versions")
    count = cursor.fetchone()[0]
    print(f"\nTotal report versions: {count}")
    
    if count > 0:
        cursor.execute("""
            SELECT rv.id, rv.report_id, rv.version_number, rv.created_at
            FROM report_versions rv
            LIMIT 5
        """)
        versions = cursor.fetchall()
        print("\nSample versions:")
        for v in versions:
            print(f"  Version {v[2]} for report {v[1]} - {v[3]}")
else:
    print("❌ report_versions table does NOT exist")

conn.close()
