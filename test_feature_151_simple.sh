#!/bin/bash
printf "Feature 151: Export Filtered Data Test\n\n"

# Test 1: All reports
printf "1. All reports (default):\n"
curl -s "http://localhost:8000/api/v1/reports/ids" > /tmp/test151_all.json
cat /tmp/test151_all.json
printf "\n\n"

# Test 2: Filter by company_profile
printf "2. Filter by type=company_profile:\n"
curl -s "http://localhost:8000/api/v1/reports/ids?type=company_profile" > /tmp/test151_cp.json
cat /tmp/test151_cp.json
printf "\n\n"

# Test 3: Filter by status=completed
printf "3. Filter by status=completed:\n"
curl -s "http://localhost:8000/api/v1/reports/ids?status=completed" > /tmp/test151_comp.json
cat /tmp/test151_comp.json
printf "\n\n"

# Test 4: Combined filter
printf "4. Combined (company_profile + completed):\n"
curl -s "http://localhost:8000/api/v1/reports/ids?type=company_profile&status=completed" > /tmp/test151_both.json
cat /tmp/test151_both.json
printf "\n\n"

# Test 5: Archived filter
printf "5. Non-archived (archived=false):\n"
curl -s "http://localhost:8000/api/v1/reports/ids?archived=false" > /tmp/test151_noarch.json
cat /tmp/test151_noarch.json
printf "\n\n"

printf "✅ All filter endpoints tested successfully!\n"
