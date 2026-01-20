import sys
sys.path.insert(0, 'backend')
from app.database import get_db_sync
from app.models.user import User

db = next(get_db_sync())
users = db.query(User).filter(User.email.like('%test%')).limit(5).all()
for user in users:
    print(f"Email: {user.email}, Role: {user.role}, 2FA: {user.two_factor_enabled}")
