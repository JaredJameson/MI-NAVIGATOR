import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check by ID
template_id = '9fc85897-2a50-4973-b6ce-e978af7189aa'
cursor.execute("SELECT id, name, type, created_at FROM report_templates WHERE id = ?", (template_id,))
template = cursor.fetchone()

if template:
    print(f"✅ Template found by ID!")
    print(f"ID: {template[0]}")
    print(f"Name: {template[1]}")
    print(f"Type: {template[2]}")
    print(f"Created: {template[3]}")
else:
    print(f"❌ Template with ID {template_id} not found")

# Also check by name
cursor.execute("SELECT id, name, created_at FROM report_templates WHERE name = 'TEST_TEMPLATE_SESSION322_REGRESSION'")
by_name = cursor.fetchone()

if by_name:
    print(f"\n✅ Also found by name!")
    print(f"ID: {by_name[0]}")
    print(f"Name: {by_name[1]}")
    print(f"Created: {by_name[2]}")

conn.close()
