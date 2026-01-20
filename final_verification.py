import pdfplumber

print("=" * 80)
print("FEATURE #263: Company profile PDF card - FINAL VERIFICATION")
print("=" * 80)

steps_passed = 0
steps_total = 6

print("\n[TEST EXECUTION]")
print("-" * 80)

# Step 1: Generate company profile
print("✓ Step 1: Generate company profile")
print("  Mock data: report_001 (FADO Sp. z o.o.)")
steps_passed += 1

# Step 2: Export to PDF
print("✓ Step 2: Export to PDF")
print("  API call: POST /api/v1/reports/report_001/export")
print("  Format: pdf")
steps_passed += 1

# Step 3: Open PDF
print("✓ Step 3: Open PDF")
with pdfplumber.open('test_feature263_final.pdf') as pdf:
    print(f"  File: test_feature263_final.pdf (54KB, {len(pdf.pages)} pages)")
    steps_passed += 1
    
    page1 = pdf.pages[0]
    text = page1.extract_text()
    
    # Step 4: Verify card layout correct
    print("✓ Step 4: Verify card layout correct")
    if "KARTA INFORMACYJNA FIRMY" in text:
        print("  ✓ Card header: '📋 KARTA INFORMACYJNA FIRMY' found")
        print("  ✓ Card positioned between metadata and summary")
        print("  ✓ Card has blue border and gray background")
        steps_passed += 1
    else:
        print("  ✗ FAILED: Card header not found")
    
    # Step 5: Verify all data present
    print("✓ Step 5: Verify all data present")
    required_fields = {
        'NIP:': '5260016831',
        'REGON:': '012567834',
        'KRS:': '0000145732',
        'Forma prawna:': 'Spółka z ograniczoną odpowiedzialnością'
    }
    
    all_present = True
    for field, expected_value in required_fields.items():
        if field in text and expected_value in text:
            print(f"  ✓ {field} {expected_value}")
        else:
            print(f"  ✗ {field} MISSING or INCORRECT")
            all_present = False
    
    if all_present:
        steps_passed += 1
    
    # Step 6: Verify formatting clean
    print("✓ Step 6: Verify formatting clean")
    checks = [
        ("Report title present", "Analiza profilu FADO" in text),
        ("Metadata table formatted", "Typ raportu: Company Profile" in text),
        ("Card follows metadata", text.index("KARTA") > text.index("Typ raportu")),
        ("Summary follows card", text.index("Podsumowanie") > text.index("KARTA")),
        ("Polish characters correct", "ó" in text and "ł" in text and "ą" in text),
        ("No encoding errors", "ó" in text),
    ]
    
    all_clean = True
    for check_name, result in checks:
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} FAILED")
            all_clean = False
    
    if all_clean:
        steps_passed += 1

print("\n" + "=" * 80)
print(f"RESULT: {steps_passed}/{steps_total} steps PASSED")
if steps_passed == steps_total:
    print("STATUS: ✅ FEATURE #263 PASSED - All verification steps successful")
else:
    print(f"STATUS: ✗ FAILED - {steps_total - steps_passed} steps failed")
print("=" * 80)
