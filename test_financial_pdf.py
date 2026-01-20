#!/usr/bin/env python3
"""Test script for Feature #264 - Financial tables in PDF"""

import requests
import subprocess
import os

# Test Step 1: Request PDF export for report with financial data
print("=== Feature #264: Financial Tables in PDF ===\n")

print("Step 1: Requesting PDF export for report_001 (FADO financial analysis)...")

# Direct API call to export endpoint
response = requests.post(
    "http://localhost:8000/api/v1/reports/report_001/export",
    json={"format": "pdf"},
    stream=True
)

if response.status_code != 200:
    print(f"❌ FAILED: Got status {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

print("✅ PASSED: PDF export endpoint returned 200")

# Step 2: Save PDF to file
print("\nStep 2: Saving PDF to file...")
pdf_path = "/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/test_feature264_financial.pdf"

with open(pdf_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

file_size = os.path.getsize(pdf_path)
print(f"✅ PASSED: PDF saved to {pdf_path} ({file_size} bytes)")

# Step 3: Verify PDF can be opened
print("\nStep 3: Verifying PDF structure with pdfinfo...")
try:
    result = subprocess.run(
        ["pdfinfo", pdf_path],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        print("✅ PASSED: PDF is valid and can be opened")
        print("\nPDF Info:")
        print(result.stdout)
    else:
        print(f"❌ FAILED: pdfinfo returned error: {result.stderr}")
        exit(1)

except FileNotFoundError:
    print("⚠️  WARNING: pdfinfo not available, skipping structure check")
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

# Step 4: Extract text to verify financial data is present
print("\nStep 4: Extracting text to verify financial tables...")
try:
    result = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        text = result.stdout

        # Check for financial data presence
        checks = {
            "Analiza finansowa": "Section title present",
            "45,2 mln PLN": "Revenue 2023",
            "Przychody": "Revenue label",
            "ROE": "Financial ratio ROE",
            "2021": "Historical data year 1",
            "2022": "Historical data year 2",
            "2023": "Historical data year 3",
        }

        print("\nChecking for financial data in PDF text:")
        all_found = True
        for keyword, description in checks.items():
            if keyword in text:
                print(f"  ✅ Found: {description} ('{keyword}')")
            else:
                print(f"  ❌ Missing: {description} ('{keyword}')")
                all_found = False

        if all_found:
            print("\n✅ PASSED: All financial data found in PDF")
        else:
            print("\n❌ FAILED: Some financial data missing from PDF")
            print("\n--- Full extracted text (first 2000 chars) ---")
            print(text[:2000])
            exit(1)

    else:
        print(f"❌ FAILED: pdftotext returned error: {result.stderr}")
        exit(1)

except FileNotFoundError:
    print("⚠️  WARNING: pdftotext not available, skipping text extraction")
except Exception as e:
    print(f"❌ FAILED: {e}")
    exit(1)

print(f"\n{'='*50}")
print("✅ SUCCESS: PDF generated successfully!")
print(f"{'='*50}")
print(f"\nManual verification steps:")
print(f"1. Open PDF: evince {pdf_path}")
print(f"2. Check financial tables formatting")
print(f"3. Verify numbers are aligned")
print(f"4. Verify no text is cut off")
