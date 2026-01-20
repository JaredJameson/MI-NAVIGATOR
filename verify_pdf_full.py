import pdfplumber

print("=" * 80)
print("FEATURE #263 VERIFICATION REPORT")
print("=" * 80)

with pdfplumber.open('test_feature263_company_profile.pdf') as pdf:
    print(f"\n✓ Step 3: PDF opened successfully")
    print(f"  Total pages: {len(pdf.pages)}")
    
    # Step 4: Verify card layout
    print("\n✓ Step 4: Verifying card layout...")
    page1 = pdf.pages[0]
    text = page1.extract_text()
    
    if "KARTA INFORMACYJNA FIRMY" in text:
        print("  ✓ Company profile card header found")
    else:
        print("  ✗ Company profile card header NOT found")
    
    # Step 5: Verify all data present
    print("\n✓ Step 5: Verifying all data present...")
    required_fields = ['NIP:', 'REGON:', 'KRS:', 'Forma prawna:']
    for field in required_fields:
        if field in text:
            print(f"  ✓ {field} present")
        else:
            print(f"  ✗ {field} MISSING")
    
    # Extract actual values
    lines = text.split('\n')
    print("\n  Extracted values:")
    for line in lines:
        if any(field in line for field in ['NIP:', 'REGON:', 'KRS:', 'Forma prawna:']):
            print(f"    {line.strip()}")
    
    # Step 6: Verify formatting
    print("\n✓ Step 6: Verifying formatting...")
    if "Typ raportu:" in text and "Company Profile" in text:
        print("  ✓ Report type metadata displayed")
    if "Podsumowanie" in text:
        print("  ✓ Summary section follows card")
    
    print("\n" + "=" * 80)
    print("FULL PAGE 1 CONTENT:")
    print("=" * 80)
    print(text)

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
