import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.core.security import get_password_hash
import uuid
from datetime import datetime

db = SessionLocal()

# Create test user with no data
user_id = str(uuid.uuid4())
email = f"emptytest_{int(datetime.now().timestamp())}@example.com"
new_user = User(
    id=user_id,
    email=email,
    password_hash=get_password_hash("Test1234!"),
    name="Empty Test User",
    role="user",
    is_active=True,
    onboarding_completed=True,
    created_at=datetime.utcnow()
)

db.add(new_user)
db.commit()

print(f"Created user: {email}")
print(f"Password: Test1234!")
print(f"User ID: {user_id}")

db.close()
