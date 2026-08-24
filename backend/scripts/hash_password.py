"""
Utility script to hash a password using PBKDF2-HMAC-SHA256.
Usage: python -m backend.scripts.hash_password <your_password>
"""
import sys
from backend.services.auth_service import hash_password, verify_password


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.scripts.hash_password <plain_password>")
        sys.exit(1)
    
    plain_password = sys.argv[1]
    pwd_hash = hash_password(plain_password)
    print("\n--- PBKDF2 PASSWORD HASH GENERATED ---")
    print(f"Password: {plain_password}")
    print(f"Hash:     {pwd_hash}")
    print(f"Verified: {verify_password(plain_password, pwd_hash)}")
    print("--------------------------------------\n")


if __name__ == "__main__":
    main()
