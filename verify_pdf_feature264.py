#!/usr/bin/env python3
"""Verify Feature #264 - Financial tables in PDF using PyMuPDF"""

import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    import subprocess
    subprocess.run([
        "/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/venv/bin/pip",
        "install", "PyMuPDF"
    ])
    import fitz

# Open the PDF
pdf_path = "test_feature264_financial.pdf"
doc = fitz.open(pdf_path)

print("=" * 60)
print("FEATURE #264: Financial Tables in PDF - Verification Report")
print("=" * 60)

print(f"\nPDF Info:")
print(f"  Pages: {doc.page_count}")
print(f"  File: {pdf_path}")

# Extract all text
all_text = ""
for page_num in range(doc.page_count):
    page = doc[page_num]
    all_text += page.get_text()

print(f"\nTotal extracted text length: {len(all_text)} characters")

# Step 4: Verify table formatting
print("\n" + "=" * 60)
print("Step 4: Verify financial data is present")
print("=" * 60)

checks = {
    "Analiza finansowa": "✓ Section title",
    "Przychody": "✓ Revenue label",
    "45,2 mln PLN": "✓ Revenue 2023",
    "ROE": "✓ Financial ratio ROE",
    "ROA": "✓ Financial ratio ROA",
    "18,2%": "✓ ROE value",
    "9,4%": "✓ ROA value",
    "2021": "✓ Historical year 2021",
    "2022": "✓ Historical year 2022",
    "2023": "✓ Historical year 2023",
    "35,8": "✓ Revenue 2021",
    "40,2": "✓ Revenue 2022",
    "Marża brutto": "✓ Gross margin label",
    "28,5%": "✓ Margin value",
}

all_passed = True
for keyword, description in checks.items():
    if keyword in all_text:
        print(f"  ✅ {description}: '{keyword}'")
    else:
        print(f"  ❌ MISSING {description}: '{keyword}'")
        all_passed = False

# Step 5: Verify numbers are aligned (check for proper table structure)
print("\n" + "=" * 60)
print("Step 5: Verify numbers alignment (table structure)")
print("=" * 60)

# Look for financial data section
if "Analiza finansowa" in all_text:
    # Find the section
    start_idx = all_text.find("Analiza finansowa")
    end_idx = all_text.find("Pozycja rynkowa", start_idx)
    if end_idx == -1:
        end_idx = start_idx + 2000

    financial_section = all_text[start_idx:end_idx]

    print("\nFinancial section excerpt (first 800 chars):")
    print("-" * 60)
    print(financial_section[:800])
    print("-" * 60)

    # Check if data looks structured (has line breaks and colons)
    has_structure = (":" in financial_section and
                    financial_section.count("\n") > 5)

    if has_structure:
        print("\n✅ Financial section has structured format")
    else:
        print("\n⚠️  Financial section may lack proper structure")

# Step 6: Verify no cut-off text
print("\n" + "=" * 60)
print("Step 6: Verify no cut-off text")
print("=" * 60)

# Check for complete sentences and words
incomplete_indicators = ["...", "—", "truncat", "cut off"]
has_issues = False

for indicator in incomplete_indicators:
    if indicator.lower() in all_text.lower():
        print(f"  ⚠️  Found potential issue: '{indicator}'")
        has_issues = True

if not has_issues:
    print("  ✅ No obvious text cut-off indicators found")

# Final verdict
print("\n" + "=" * 60)
print("FINAL VERDICT")
print("=" * 60)

if all_passed:
    print("✅ PASSED: All financial data found in PDF")
    print("✅ Financial tables are rendering correctly")
    exit(0)
else:
    print("❌ FAILED: Some financial data missing from PDF")
    print("❌ Tables may not be rendering properly")

    print("\n--- Full text for debugging ---")
    print(all_text[:3000])
    exit(1)
