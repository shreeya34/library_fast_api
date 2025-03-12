from datetime import datetime, timedelta
from models import Member
import uuid

def main():
    
    role = input("Enter your role (1 for Admin, 2 for Member): ")
    
    if role == "1":  # Admin role
        name = input("Enter your username:")
        password = input("Enter your password:")
        admin_id = str(uuid.uuid4)
        print(f"Generated token:{admin_id}")
        
if __name__ == "__main__":
    main()
        