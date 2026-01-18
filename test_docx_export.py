#!/usr/bin/env python3
"""
Test script to verify DOCX export functionality
"""
import sys
import asyncio
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.api.v1.endpoints.reports import MOCK_REPORTS, export_to_docx

async def test_docx_export():
    """Test DOCX export with first mock report"""
    report = MOCK_REPORTS[0]

    print(f"Testing DOCX export for report: {report['id']}")
    print(f"Title: {report['title']}")
    print(f"Sections: {len(report.get('sections', []))}")

    try:
        # Call the export function
        response = await export_to_docx(report)

        # Save the file
        output_file = "/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/test_report.docx"
        with open(output_file, 'wb') as f:
            # Read from StreamingResponse
            async for chunk in response.body_iterator:
                f.write(chunk)

        print(f"\n✅ SUCCESS! DOCX file created: {output_file}")

        # Check file size
        import os
        file_size = os.path.getsize(output_file)
        print(f"File size: {file_size} bytes ({file_size / 1024:.1f} KB)")

        if file_size < 1000:
            print("⚠️  WARNING: File seems too small, might be empty or corrupted")
        else:
            print("✅ File size looks good")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_docx_export())
    sys.exit(0 if result else 1)
