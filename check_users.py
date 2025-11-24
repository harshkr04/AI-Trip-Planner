from backend.database import SessionLocal
from backend.models import User

def count_users():
    db = SessionLocal()
    try:
        count = db.query(User).count()
        print(f"User count: {count}")
        users = db.query(User).all()
        for u in users:
            print(f" - {u.email} (ID: {u.id})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    count_users()
