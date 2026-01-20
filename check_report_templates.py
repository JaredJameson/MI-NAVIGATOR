import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check for report_templates table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%template%'")
tables = cursor.fetchall()
print("Template-related tables:")
for table in tables:
    print(f"  - {table[0]}")

if tables:
    # Check for our test template
    cursor.execute("SELECT id, name, created_at FROM report_templates WHERE name = 'TEST_TEMPLATE_SESSION322_REGRESSION' ORDER BY created_at DESC")
    template = cursor.fetchone()
    
    if template:
        print(f"\n✅ Template found!")
        print(f"ID: {template[0]}")
        print(f"Name: {template[1]}")
        print(f"Created: {template[2]}")
    else:
        print("\n❌ Template 'TEST_TEMPLATE_SESSION322_REGRESSION' not found")
    
    # Show all templates
    cursor.execute("SELECT id, name, created_at FROM report_templates ORDER BY created_at DESC LIMIT 5")
    all_templates = cursor.fetchall()
    print(f"\nLast 5 templates:")
    for t in all_templates:
        print(f"  - {t[1]} (Created: {t[2]})")
else:
    print("\n⚠️ No template tables found")

conn.close()
