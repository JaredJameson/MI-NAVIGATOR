import pdfplumber

with pdfplumber.open('test_feature263_company_profile.pdf') as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    print("\n=== PAGE 1 (TITLE PAGE) ===")
    page1 = pdf.pages[0]
    text = page1.extract_text()
    print(text[:1500] if text else "No text found")
