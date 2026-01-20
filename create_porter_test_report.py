#!/usr/bin/env python3
"""Create a test report with Porter's Five Forces analysis for regression testing"""

import sqlite3
import json
from datetime import datetime

# Sample Porter analysis data
porter_data = {
    "type": "porter_analysis",
    "data": {
        "industry_name": "E-commerce (Fashion)",
        "region": "Polska",
        "analysis_date": "2026-01-20",
        "supplier_power": {
            "score": 6,
            "level": "Medium-High",
            "factors": [
                {
                    "factor": "Koncentracja dostawców",
                    "description": "Ograniczona liczba producentów odzieży premium zwiększa ich siłę przetargową",
                    "impact": "high"
                },
                {
                    "factor": "Koszty zmiany dostawcy",
                    "description": "Średnie koszty związane z testowaniem jakości i logistyką nowych dostawców",
                    "impact": "medium"
                }
            ],
            "data_source": "Industry Analysis 2026"
        },
        "buyer_power": {
            "score": 7,
            "level": "High",
            "factors": [
                {
                    "factor": "Dostępność alternatyw",
                    "description": "Klienci mają łatwy dostęp do wielu platform e-commerce",
                    "impact": "high"
                },
                {
                    "factor": "Wrażliwość cenowa",
                    "description": "Konsumenci łatwo porównują ceny online",
                    "impact": "high"
                }
            ],
            "data_source": "Consumer Behavior Study 2026"
        },
        "competitive_rivalry": {
            "score": 8,
            "level": "Very High",
            "factors": [
                {
                    "factor": "Liczba konkurentów",
                    "description": "Bardzo wysoka liczba graczy na rynku e-commerce fashion",
                    "impact": "high"
                },
                {
                    "factor": "Konkurencja cenowa",
                    "description": "Intensywne wojny cenowe i promocje",
                    "impact": "high"
                }
            ],
            "data_source": "Market Competition Report 2026"
        },
        "threat_of_substitution": {
            "score": 5,
            "level": "Medium",
            "factors": [
                {
                    "factor": "Zakupy stacjonarne",
                    "description": "Tradycyjne sklepy nadal stanowią alternatywę",
                    "impact": "medium"
                },
                {
                    "factor": "Second-hand market",
                    "description": "Rosnący rynek odzieży używanej",
                    "impact": "medium"
                }
            ],
            "data_source": "Retail Trends Analysis 2026"
        },
        "threat_of_new_entry": {
            "score": 4,
            "level": "Medium-Low",
            "factors": [
                {
                    "factor": "Niskie bariery technologiczne",
                    "description": "Łatwo uruchomić sklep online z gotowych platform",
                    "impact": "high"
                },
                {
                    "factor": "Wymagany kapitał marketingowy",
                    "description": "Wysokie koszty pozyskania klienta i budowy marki",
                    "impact": "medium"
                }
            ],
            "data_source": "Market Entry Analysis 2026"
        },
        "overall_assessment": {
            "average_score": 6.0,
            "industry_attractiveness": "Średnia atrakcyjność",
            "summary": "Branża e-commerce fashion charakteryzuje się wysoką konkurencją i silną pozycją nabywców, co obniża jej atrakcyjność. Umiarkowane zagrożenia substytutami i nowymi wejściami częściowo równoważą negatywne aspekty.",
            "key_recommendations": [
                "Zbuduj silną markę aby zmniejszyć wrażliwość cenową klientów",
                "Dywersyfikuj bazę dostawców aby zmniejszyć ich siłę przetargową",
                "Inwestuj w program lojalnościowy aby zwiększyć koszty zmiany dla klientów",
                "Rozważ niszowanie się w segmencie premium lub specjalistycznym"
            ]
        },
        "data_sources": [
            {"name": "GUS E-commerce Report", "confidence": 0.9},
            {"name": "Euromonitor Retail Analysis", "confidence": 0.85},
            {"name": "Industry Interviews", "confidence": 0.75}
        ]
    }
}

# Connect to database
conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

# Create report
report_id = 'porter_test_regression_268'
title = 'TEST PORTER ANALYSIS - E-commerce Fashion'
report_type = 'market_analysis'
status = 'completed'
created_at = datetime.now().isoformat()

# Insert report
cursor.execute("""
    INSERT INTO reports (id, title, report_type, status, content, created_at, updated_at, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    report_id,
    title,
    report_type,
    status,
    json.dumps(porter_data),
    created_at,
    created_at,
    1  # Assuming user_id 1 exists
))

conn.commit()
print(f"✅ Created test report: {report_id}")
print(f"   Title: {title}")
print(f"   URL: http://localhost:3000/reports/{report_id}")

conn.close()
