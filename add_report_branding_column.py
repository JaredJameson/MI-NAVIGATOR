"""
Add report_branding column to users table - Feature #220
"""
import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

try:
    # Add report_branding column (default True = show logo)
    cursor.execute('''
        ALTER TABLE users
        ADD COLUMN report_branding INTEGER DEFAULT 1
    ''')
    conn.commit()
    print("✓ Successfully added report_branding column to users table")
    print("  Default value: 1 (True = include logo in reports)")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("✓ Column report_branding already exists")
    else:
        print(f"✗ Error: {e}")
finally:
    conn.close()
