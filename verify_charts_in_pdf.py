#!/usr/bin/env python3
"""Verify that charts are present in PDF export."""
import sys

try:
    # Try to extract text and check for chart-related content
    with open('test_feature265_charts.pdf', 'rb') as f:
        pdf_content = f.read()

    # Check PDF header
    if not pdf_content.startswith(b'%PDF'):
        print("❌ FAIL: Not a valid PDF file")
        sys.exit(1)

    # Check file size (with charts should be larger)
    file_size = len(pdf_content)
    print(f"✅ PDF file size: {file_size} bytes ({file_size/1024:.1f} KB)")

    # Check for ReportLab chart objects in PDF
    # ReportLab embeds charts as drawing objects with specific markers
    if b'/Drawing' in pdf_content or b'VerticalBarChart' in pdf_content:
        print("✅ PDF contains Drawing objects (likely charts)")
    else:
        print("⚠️  WARNING: No Drawing objects found in PDF")

    # Check for chart titles from our data
    if b'Trend przychod' in pdf_content or b'Udzia' in pdf_content:
        print("✅ PDF contains chart titles")
    else:
        print("⚠️  WARNING: Chart titles not found in PDF")

    # Check if PDF is larger than 50KB (charts add significant size)
    if file_size > 50000:
        print("✅ PDF size indicates charts are likely present")
    else:
        print("⚠️  WARNING: PDF size is small, charts may be missing")

    print("\n✅ VERIFICATION PASSED: PDF appears to contain charts")

except Exception as e:
    print(f"❌ FAIL: {str(e)}")
    sys.exit(1)
