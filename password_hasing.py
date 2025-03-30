from argon2 import PasswordHasher

# Create the PasswordHasher instance
password_hasher = PasswordHasher()

# Function to hash a password
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def check_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, password)
    except Exception as e:
        return False
