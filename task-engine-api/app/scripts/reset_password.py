from app.db.deps import get_db
from app.models import User
from app.core.security import hash_password

def main():
    db = next(get_db())  # get_db generator
    try:
        user = db.query(User).filter(User.email == "test3@acme.com").first()
        if not user:
            print("User not found")
            return

        user.hashed_password = hash_password("123456")
        db.commit()
        print("OK: password updated -> test3@acme.com / 123456")
    finally:
        db.close()

if __name__ == "__main__":
    main()