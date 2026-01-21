import sqlite3

conn = sqlite3.connect('assistant.db')
cur = conn.cursor()

cur.execute("SELECT * FROM features WHERE id = 57")
feature = cur.fetchone()

if feature:
    print(f"ID: {feature[0]}")
    print(f"Priority: {feature[1]}")
    print(f"Category: {feature[2]}")
    print(f"Name: {feature[3]}")
    print(f"Description: {feature[4]}")
    print(f"Steps: {feature[5]}")
    print(f"Passes: {feature[6]}")
    print(f"In Progress: {feature[7]}")

cur.close()
conn.close()
