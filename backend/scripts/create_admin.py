"""Create or promote an administrator account.

Run from the backend container:
python scripts/create_admin.py admin@example.com 'StrongPassword123' 'Admin Name'
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: python scripts/create_admin.py EMAIL PASSWORD NAME")
    email, password, name = sys.argv[1], sys.argv[2], sys.argv[3]
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email.strip().lower()))
        if user is None:
            user = User(name=name.strip(), email=email.strip().lower(), password_hash=hash_password(password), role=UserRole.ADMIN)
            db.add(user)
        else:
            user.role = UserRole.ADMIN
        db.commit()
        print(f"Administrator ready: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
