from passlib.context import CryptContext
import sys

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("testpassword")
    print(f"Hash created successfully: {hash}")
    print("Passlib and bcrypt are working.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
