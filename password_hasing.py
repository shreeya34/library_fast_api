from argon2 import PasswordHasher

password = PasswordHasher()

def hash_password(password: str) -> str:
    return password.hash(password)

def check_password(password: str, hashed_password: str) -> bool:
    try:
        return password.verify(hashed_password, password)
    except:
        return False
    
