from datetime import datetime, timedelta
from models import Member
import uuid
import requests
import json

def main():
    
    role = input("Enter your role (1 for Admin, 2 for Member): ")
    
    if role == "1":  # Admin role
        name = input("Enter your username:")
        password = input("Enter your password:")
        admin_id = str(uuid.uuid4)
        print(f"Generated token:{admin_id}")
        response = requests.post("http://127.0.0.1:8000/admin/")
        if response == 200:
            print("Admin data created sucessfully")
        else:
            print("error")
        
       
        
if __name__ == "__main__":
    main()
        