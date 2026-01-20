import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Sprawdź użytkownika
cursor.execute('SELECT id, email, name FROM users WHERE email = ?', ('user@example.com',))
user = cursor.fetchone()
print(f'User: {user}')

if user:
    user_id = user[0]
    # Sprawdź raporty tego użytkownika
    cursor.execute('SELECT id, title, owner_id FROM reports WHERE owner_id = ? LIMIT 5', (user_id,))
    reports = cursor.fetchall()
    print(f'\nUser reports (first 5): {reports}')
    
    # Sprawdź pierwszy raport pagination
    cursor.execute('SELECT id, title, owner_id FROM reports WHERE id = ?', ('pagination_test_0001',))
    test_report = cursor.fetchone()
    print(f'\nPagination test report 0001: {test_report}')
    
    # Sprawdź czy są duplikaty tego ID
    cursor.execute('SELECT COUNT(*) FROM reports WHERE id = ?', ('pagination_test_0001',))
    count = cursor.fetchone()[0]
    print(f'\nNumber of reports with ID "pagination_test_0001": {count}')
    
    # Sprawdź wszystkie raporty z tym ID
    cursor.execute('SELECT id, title, owner_id FROM reports WHERE id = ?', ('pagination_test_0001',))
    all_test_reports = cursor.fetchall()
    print(f'\nAll reports with ID "pagination_test_0001": {all_test_reports}')

conn.close()
