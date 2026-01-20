import pdfplumber

print("=" * 80)
print("FINAL FEATURE #263 VERIFICATION - WITH POLISH FONTS")
print("=" * 80)

with pdfplumber.open('test_feature263_final.pdf') as pdf:
    print(f"\n✓ PDF opened - {len(pdf.pages)} pages")
    
    page1 = pdf.pages[0]
    text = page1.extract_text()
    
    print("\n📋 COMPANY PROFILE CARD CONTENT:")
    print("=" * 80)
    
    lines = text.split('\n')
    in_card = False
    for line in lines:
        if 'KARTA INFORMACYJNA' in line:
            in_card = True
        if in_card:
            print(line)
        if in_card and 'Podsumowanie' in line:
            break
    
    # Test for Polish characters
    print("\n🔤 POLISH CHARACTERS TEST:")
    print("=" * 80)
    if 'ó' in text or 'ł' in text or 'ą' in text:
        print("✓ Polish characters detected in PDF")
        # Find line with "Forma prawna"
        for line in lines:
            if 'Forma prawna' in line:
                print(f"  {line}")
    else:
        print("✗ No Polish characters - fallback to Helvetica")
