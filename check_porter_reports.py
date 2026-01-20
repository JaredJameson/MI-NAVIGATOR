import sqlite3

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

# Sprawdź czy są raporty z Portera
cursor.execute("""
    SELECT id, title, report_type, status, content
    FROM reports
    WHERE content LIKE '%Porter%' OR content LIKE '%Five Forces%' OR title LIKE '%Porter%'
    LIMIT 5
""")

reports = cursor.fetchall()
if reports:
    print(f"Znaleziono {len(reports)} raportów z analizą Portera:\n")
    for r in reports:
        print(f"ID: {r[0]}, Title: {r[1]}, Type: {r[2]}, Status: {r[3]}")
        print(f"Content preview: {r[4][:200] if r[4] else 'No content'}...\n")
else:
    print("Brak raportów z analizą Portera w bazie danych")

# Sprawdź czy są jakiekolwiek raporty
cursor.execute("SELECT COUNT(*) FROM reports")
total = cursor.fetchone()[0]
print(f"\nŁącznie raportów w bazie: {total}")

conn.close()
