import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Get user ID
cursor.execute("SELECT id FROM users WHERE email = 'test@example.com'")
user_row = cursor.fetchone()

if user_row:
    user_id = user_row[0]
    print(f"User ID: {user_id}")
    
    # Get latest reset token
    cursor.execute("""
        SELECT token, created_at, expires_at 
        FROM password_reset_tokens 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (user_id,))
    
    token_row = cursor.fetchone()
    if token_row:
        print(f"\nReset Token: {token_row[0]}")
        print(f"Created: {token_row[1]}")
        print(f"Expires: {token_row[2]}")
        print(f"\nReset Link: http://localhost:3000/auth/reset-password?token={token_row[0]}")
    else:
        print("No reset token found")
else:
    print("User not found")

conn.close()
