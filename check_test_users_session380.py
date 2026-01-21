from app.db import get_db
from app.models import User

db = next(get_db())
users = db.query(User).filter(User.email.like('test_session379%')).all()

if users:
    print("Test users from session 379:")
    for u in users:
        print(f"  - {u.email}")
else:
    print("No test users found from session 379")
