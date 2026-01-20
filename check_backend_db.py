import sqlite3

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

# Check for our test template
cursor.execute("SELECT id, name, type, created_at FROM report_templates WHERE name = 'TEST_TEMPLATE_SESSION322_REGRESSION'")
template = cursor.fetchone()

if template:
    print(f"✅ Template found in backend DB!")
    print(f"ID: {template[0]}")
    print(f"Name: {template[1]}")
    print(f"Type: {template[2]}")
    print(f"Created: {template[3]}")
else:
    print(f"❌ Template not found in backend DB")

# Count all templates
cursor.execute("SELECT COUNT(*) FROM report_templates")
total = cursor.fetchone()[0]
print(f"\nTotal templates in backend DB: {total}")

conn.close()
