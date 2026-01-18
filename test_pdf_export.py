"""
Direct test of PDF export functionality
"""
import sys
sys.path.insert(0, 'backend')

import asyncio
from backend.app.api.v1.endpoints.reports import export_to_pdf, MOCK_REPORTS

async def test_pdf():
    # Get first report
    report = MOCK_REPORTS[0]
    print(f"Testing PDF export for report: {report['id']}")
    print(f"Title: {report['title']}")

    # Call export function
    response = await export_to_pdf(report)

    # Save to file
    content = b''
    async for chunk in response.body_iterator:
        content += chunk

    output_path = 'test_export_output.pdf'
    with open(output_path, 'wb') as f:
        f.write(content)

    print(f"\n✅ PDF generated successfully!")
    print(f"📄 File saved to: {output_path}")
    print(f"📊 File size: {len(content)} bytes")

    return output_path

if __name__ == "__main__":
    asyncio.run(test_pdf())
