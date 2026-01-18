#!/usr/bin/env python3
"""Test PPTX export functionality directly."""

import sys
import os

# Add backend to path
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.api.v1.endpoints.reports import export_to_pptx
import asyncio

# Mock report data (same structure as MOCK_REPORTS)
mock_report = {
    "id": "report_test_pptx",
    "title": "Test PPTX Export - Analiza FADO",
    "type": "company_profile",
    "company": "FADO Sp. z o.o.",
    "created_at": "2026-01-18T12:00:00",
    "updated_at": "2026-01-18T12:30:00",
    "summary": "To jest testowy raport do weryfikacji eksportu PPTX.\n\nRaport zawiera kilka sekcji z różnymi formatami treści:\n- Punkty wypunktowane\n- Listy numerowane\n- Pogrubiony tekst\n\nDziała poprawnie!",
    "sections": [
        {
            "id": "section_1",
            "title": "Informacje podstawowe",
            "content": "FADO Sp. z o.o. to polska firma założona w 1998 roku.\n\n**Dane rejestrowe:**\n- NIP: 5260016831\n- REGON: 012567834\n- KRS: 0000145732\n\nFirma zatrudnia około 150 pracowników."
        },
        {
            "id": "section_2",
            "title": "Analiza finansowa",
            "content": "**Przychody (2023):**\n1. Przychody ze sprzedaży: 45,2 mln PLN\n2. Wzrost r/r: +12,3%\n3. Marża brutto: 28,5%\n\n**Wskaźniki:**\n- ROE: 18,2%\n- ROA: 9,4%\n- Płynność: 2,1"
        },
        {
            "id": "section_3",
            "title": "Podsumowanie",
            "content": "**Wnioski końcowe:**\n\nFirma wykazuje stabilny wzrost i dobrą kondycję finansową.\n\nZalecenia:\n1. Kontynuacja obecnej strategii\n2. Monitorowanie konkurencji\n3. Ekspansja na nowe rynki"
        }
    ]
}

async def test_pptx_export():
    """Test PPTX export function."""
    print("Testing PPTX export functionality...")
    print(f"Report title: {mock_report['title']}")
    print(f"Sections: {len(mock_report['sections'])}")

    try:
        # Call export function
        response = await export_to_pptx(mock_report)

        print("\n✅ PPTX export function executed successfully!")
        print(f"Response type: {type(response)}")
        print(f"Media type: {response.media_type}")
        print(f"Headers: {response.headers}")

        # Check if it's a StreamingResponse
        if hasattr(response, 'body_iterator'):
            # Read the content
            content = b''
            async for chunk in response.body_iterator:
                content += chunk

            file_size = len(content)
            print(f"File size: {file_size} bytes ({file_size / 1024:.2f} KB)")

            # Verify it's a valid PPTX file (check magic bytes)
            if content[:4] == b'PK\x03\x04':
                print("✅ Valid ZIP/PPTX file signature detected")
            else:
                print("❌ Invalid file signature")
                return False

            # Check for PPTX-specific files in the archive
            if b'ppt/presentation.xml' in content or b'ppt/' in content:
                print("✅ PPTX structure detected")
            else:
                print("⚠️  PPTX structure not clearly identified")

            # Save to file for manual inspection
            output_file = '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/test_report.pptx'
            with open(output_file, 'wb') as f:
                f.write(content)
            print(f"\n✅ PPTX file saved to: {output_file}")
            print("You can open this file in PowerPoint to verify slides.")

            return True
        else:
            print("❌ Response is not a StreamingResponse")
            return False

    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_pptx_export())
    sys.exit(0 if result else 1)
