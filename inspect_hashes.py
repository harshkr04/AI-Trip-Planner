from backend.database import SessionLocal
from backend.models import User

def inspect_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            pw_preview = u.hashed_password[:10] + "..." if u.hashed_password else "NONE"
            print(f"Email: {u.email}, Hash: {pw_preview}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_users()
