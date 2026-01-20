import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.database import get_db
from app.models.user import User

db = next(get_db())
user = db.query(User).filter(User.email == "test_session355@example.com").first()

if user:
    print(f"User exists: {user.email} (ID: {user.id})")
else:
    print("User does not exist - will create")
db.close()
