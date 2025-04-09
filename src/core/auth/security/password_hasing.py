import string
import random


from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def check_password(password: str, hashed_password: str) -> bool:
    try:
        print(
            f"Verifying password... \nEntered password: {password} \nHashed password: {hashed_password}"
        )

        is_valid = password_hasher.verify(hashed_password, password)

        print(f"Password verification result: {is_valid}")

        return is_valid
    except Exception as e:
        print(f"Password verification failed: {e}")
        return False


def generate_random_password(length: int = 12) -> str:
    characters = string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))
