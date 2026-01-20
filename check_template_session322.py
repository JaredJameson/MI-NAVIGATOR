import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check if templates table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")
tables = cursor.fetchall()
print(f"Templates table exists: {len(tables) > 0}")

if len(tables) > 0:
    # Check for our test template
    cursor.execute("SELECT id, name, created_at FROM templates WHERE name = 'TEST_TEMPLATE_SESSION322_REGRESSION'")
    template = cursor.fetchone()
    
    if template:
        print(f"\n✅ Template found!")
        print(f"ID: {template[0]}")
        print(f"Name: {template[1]}")
        print(f"Created: {template[2]}")
    else:
        print("\n❌ Template not found in database")
    
    # Show all templates
    cursor.execute("SELECT id, name, created_at FROM templates ORDER BY created_at DESC LIMIT 5")
    all_templates = cursor.fetchall()
    print(f"\nLast 5 templates:")
    for t in all_templates:
        print(f"  - {t[1]} (ID: {t[0]}, Created: {t[2]})")
else:
    print("\n⚠️ Templates table does not exist")

conn.close()
