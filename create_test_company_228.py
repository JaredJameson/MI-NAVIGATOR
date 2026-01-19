#!/usr/bin/env python3
"""Create test company for Feature #228 - Source reliability indicator"""

import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.database import get_db
from sqlalchemy.orm import Session

# Get database session
db = next(get_db())

# Check if companies table exists and has data
from sqlalchemy import text

try:
    result = db.execute(text("SELECT COUNT(*) FROM companies")).fetchone()
    print(f"Total companies in DB: {result[0]}")

    # Get first company if exists
    if result[0] > 0:
        company = db.execute(text("SELECT id, name, nip FROM companies LIMIT 1")).fetchone()
        print(f"\nFirst company:")
        print(f"  ID: {company[0]}")
        print(f"  Name: {company[1]}")
        print(f"  NIP: {company[2]}")
    else:
        print("\nNo companies found. Creating test company...")

        # Insert test company
        db.execute(text("""
            INSERT INTO companies (id, name, nip, regon, krs, legal_form, industry, created_at, updated_at)
            VALUES (
                'test-reliability-228',
                'Test Company dla Feature 228',
                '1234567890',
                '123456789',
                '0000123456',
                'Sp. z o.o.',
                'IT/Software',
                datetime('now'),
                datetime('now')
            )
        """))
        db.commit()
        print("✅ Test company created: test-reliability-228")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

db.close()
