from argon2 import PasswordHasher

# Create the PasswordHasher instance
password_hasher = PasswordHasher()

# Function to hash a password
def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def check_password(password: str, hashed_password: str) -> bool:
    try:
        # Log the values to ensure correct data is being passed
        print(f"Verifying password... \nEntered password: {password} \nHashed password: {hashed_password}")
        
        # Verify if the entered password matches the hashed password
        is_valid = password_hasher.verify(hashed_password, password)
        
        # Log the result
        print(f"Password verification result: {is_valid}")
        
        return is_valid
    except Exception as e:
        print(f"Password verification failed: {e}")
        return False

