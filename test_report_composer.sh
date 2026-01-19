#!/bin/bash

# Test Report Composer - Feature #158
# Tests comprehensive report composition from multiple agent outputs

set -e

API_URL="http://localhost:8000/api/v1"

echo "========================================"
echo "Feature #158: Report Composer Aggregates Sections"
echo "========================================"
echo ""

# Step 1: Get authentication token
echo "=== Step 1: Authentication ==="
cat > /tmp/login_composer.json << 'EOF'
{
  "username": "insight_test@example.com",
  "password": "Test123!"
}
EOF

TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d @/tmp/login_composer.json | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Authentication failed"
  exit 1
fi

echo "✅ Authenticated successfully"
echo ""

# Step 2: Run comprehensive analysis (compose report from multiple sections)
echo "=== Step 2: Compose Report from Multiple Sections ==="

cat > /tmp/compose_request.json << 'EOF'
{
  "company_name": "TechVision Sp. z o.o.",
  "sections": {
    "company_profile": {
      "legal_form": "Spółka z ograniczoną odpowiedzialnością",
      "founded_year": 2018,
      "industry": "Technologie informatyczne",
      "nip": "9876543210",
      "krs": "0000987654",
      "address": "ul. Innowacyjna 15, 00-001 Warszawa"
    },
    "financial_analysis": {
      "metrics": {
        "revenue": 25000000,
        "revenue_growth": 35.8,
        "profit_margin": 22.5,
        "debt_to_equity": 0.4,
        "current_ratio": 3.2
      },
      "sources": [
        {
          "type": "financial_report",
          "name": "Sprawozdanie finansowe 2023",
          "url": "https://ekrs.pl/987654",
          "confidence": 95
        }
      ]
    },
    "market_analysis": {
      "market_size": 5000000000,
      "market_growth": 15.2,
      "market_share": 3.5,
      "sources": [
        {
          "type": "market_report",
          "name": "Rynek IT w Polsce 2024",
          "url": "https://example.com/report",
          "confidence": 85
        }
      ]
    },
    "insights": [
      {
        "title": "Bardzo silny wzrost przychodów",
        "description": "Firma notuje 35.8% wzrost przychodów rok do roku, znacznie powyżej średniej branżowej",
        "type": "opportunity",
        "impact": "high",
        "data_backed": true,
        "source_metric": "revenue_growth: 35.8%"
      },
      {
        "title": "Wysoka rentowność",
        "description": "Marża zysku netto 22.5% wskazuje na bardzo efektywne zarządzanie kosztami",
        "type": "opportunity",
        "impact": "high",
        "data_backed": true,
        "source_metric": "profit_margin: 22.5%"
      },
      {
        "title": "Niska dźwignia finansowa",
        "description": "Wskaźnik zadłużenia 0.4 sugeruje konserwatywne finansowanie i potencjał do wzrostu przez dług",
        "type": "opportunity",
        "impact": "medium",
        "data_backed": true,
        "source_metric": "debt_to_equity: 0.4"
      }
    ],
    "opportunities": [
      {
        "title": "Ekspansja na rynki zagraniczne",
        "description": "Silna pozycja finansowa umożliwia ekspansję na rynki CEE",
        "impact": "high",
        "timeline": "medium_term",
        "related_insights": [0, 1]
      },
      {
        "title": "Akwizycje mniejszych konkurentów",
        "description": "Niska dźwignia finansowa pozwala na finansowanie przejęć",
        "impact": "high",
        "timeline": "short_term",
        "related_insights": [2]
      }
    ],
    "risks": [
      {
        "title": "Wysoka konkurencja w segmencie IT",
        "description": "Rynek IT w Polsce charakteryzuje się wysoką konkurencją i niskimi barierami wejścia",
        "severity": "medium",
        "likelihood": "high",
        "data_backed": true,
        "mitigation_strategies": [
          "Różnicowanie oferty poprzez specjalizację",
          "Budowanie długoterminowych relacji z kluczowymi klientami",
          "Inwestycja w unikalne kompetencje technologiczne"
        ]
      }
    ],
    "recommendations": [
      {
        "title": "Przyspieszenie ekspansji zagranicznej",
        "description": "Wykorzystać silną pozycję finansową do wejścia na rynki CEE, szczególnie Czechy i Słowację",
        "priority": "high",
        "timeline": "short_term",
        "expected_impact": "Zwiększenie przychodów o 40-50% w ciągu 2 lat",
        "related_insights": [0, 1]
      },
      {
        "title": "Strategiczne przejęcia",
        "description": "Rozważyć przejęcie 2-3 mniejszych firm w celu szybkiego zwiększenia udziału w rynku",
        "priority": "high",
        "timeline": "medium_term",
        "expected_impact": "Wzrost udziału w rynku z 3.5% do 8-10%",
        "related_insights": [2]
      },
      {
        "title": "Zwiększenie inwestycji w R&D",
        "description": "Przeznaczyć 15% przychodów na badania i rozwój nowych technologii",
        "priority": "medium",
        "timeline": "short_term",
        "expected_impact": "Wzmocnienie przewagi konkurencyjnej",
        "related_insights": [1]
      }
    ]
  },
  "include_sources": true,
  "language": "pl"
}
EOF

RESPONSE=$(curl -s -X POST "$API_URL/analysis/compose-report" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/compose_request.json)

echo "Response preview:"
echo "$RESPONSE" | head -c 500
echo ""
echo "..."
echo ""

# Step 3: Verify report composer runs
echo "=== Step 3: Verify Report Composer Runs ==="

if echo "$RESPONSE" | grep -q '"title"'; then
  echo "✅ Report composer executed successfully"
else
  echo "❌ Report composer failed"
  echo "$RESPONSE"
  exit 1
fi
echo ""

# Step 4: Verify all sections included
echo "=== Step 4: Verify All Sections Included ==="

SECTIONS_COUNT=$(echo "$RESPONSE" | grep -o '"sections"' | wc -l)
echo "Found sections field: $SECTIONS_COUNT times"

# Check for specific sections
if echo "$RESPONSE" | grep -q '"company_profile"'; then
  echo "✅ Company profile section included"
else
  echo "❌ Company profile section missing"
fi

if echo "$RESPONSE" | grep -q '"financial_analysis"'; then
  echo "✅ Financial analysis section included"
else
  echo "❌ Financial analysis section missing"
fi

if echo "$RESPONSE" | grep -q '"insights"'; then
  echo "✅ Insights section included"
else
  echo "❌ Insights section missing"
fi

if echo "$RESPONSE" | grep -q '"recommendations"'; then
  echo "✅ Recommendations section included"
else
  echo "❌ Recommendations section missing"
fi

echo ""

# Step 5: Verify table of contents generated
echo "=== Step 5: Verify Table of Contents Generated ==="

if echo "$RESPONSE" | grep -q '"table_of_contents"'; then
  echo "✅ Table of contents generated"

  TOC_ENTRIES=$(echo "$RESPONSE" | grep -o '"section_id"' | wc -l)
  echo "   TOC entries: $TOC_ENTRIES"

  if [ "$TOC_ENTRIES" -gt 0 ]; then
    echo "✅ TOC contains entries"
  else
    echo "❌ TOC is empty"
  fi
else
  echo "❌ Table of contents not generated"
fi

echo ""

# Step 6: Verify sources cited throughout
echo "=== Step 6: Verify Sources Cited Throughout ==="

if echo "$RESPONSE" | grep -q '"sources"'; then
  echo "✅ Sources section present"

  SOURCE_COUNT=$(echo "$RESPONSE" | grep -o '"confidence"' | wc -l)
  echo "   Source references found: $SOURCE_COUNT"

  if [ "$SOURCE_COUNT" -gt 0 ]; then
    echo "✅ Sources cited in report"
  else
    echo "❌ No source citations found"
  fi
else
  echo "❌ Sources section missing"
fi

echo ""

# Step 7: Verify executive summary generated
echo "=== Step 7: Verify Executive Summary Generated ==="

if echo "$RESPONSE" | grep -q '"executive_summary"'; then
  echo "✅ Executive summary generated"

  if echo "$RESPONSE" | grep -q '"key_findings"'; then
    FINDINGS_COUNT=$(echo "$RESPONSE" | grep -o '"finding"' | wc -l)
    echo "   Key findings: $FINDINGS_COUNT"
    echo "✅ Key findings extracted"
  fi

  if echo "$RESPONSE" | grep -q '"highlights"'; then
    echo "✅ Highlights extracted"
  fi
else
  echo "❌ Executive summary not generated"
fi

echo ""

# Step 8: Verify metadata
echo "=== Step 8: Verify Report Metadata ==="

if echo "$RESPONSE" | grep -q '"metadata"'; then
  echo "✅ Metadata present"

  if echo "$RESPONSE" | grep -q '"section_count"'; then
    echo "✅ Section count tracked"
  fi

  if echo "$RESPONSE" | grep -q '"word_count"'; then
    echo "✅ Word count estimated"
  fi

  if echo "$RESPONSE" | grep -q '"analysis_depth"'; then
    echo "✅ Analysis depth determined"
  fi
else
  echo "❌ Metadata missing"
fi

echo ""

# Save full response for inspection
echo "$RESPONSE" > /tmp/report_composer_full_response.json
echo "Full response saved to /tmp/report_composer_full_response.json"
echo ""

echo "========================================"
echo "✅ Feature #158 Test Complete"
echo "========================================"
