import json
from admin import Admin
from data_handling import load_data, save_data
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
import uuid  # For generating a unique token (Optional)

class AdminLogin(BaseModel):
    name: str
    password: str

app = FastAPI()



@app.post("/login")
def login_admin(login: AdminLogin):
    file_name = "admin.json"
    data = load_data(file_name)
    
    print(f"Login Data: {login}") 

    admin_users = data.get("Admin", []) 
    
    for user in admin_users:
        if isinstance(user, dict) and login.name == user.get("name") and login.password == user.get("password"):
            member_id = user.get("member_id")
            
            new_login = {"name": login.name, "status": "success", "member_id": member_id}
            
           
            existing_logins = load_data("login.json")
            if not isinstance(existing_logins, list):
                    existing_logins = []
           
            # Append the new login data
            existing_logins.append(new_login)
            
            save_data("login.json", existing_logins)
                
            return {"message": "Login Success", "member_id": member_id}
    
    return {"message": "Invalid credentials"}
class NewMember(BaseModel):
    name: str
    role: str
    password: str
    
@app.post("/add_member")
def add_member(newuser: NewMember, request: Request):
    print(f"Request Headers: {request.headers}")

    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    if not auth_header or "Bearer " not in auth_header:
        print("No token received or incorrect format!")
        

    token = auth_header.replace("Bearer ", "").strip()
    print(f"Received token: {token}")

    admin_data = load_data("admin.json")
    if isinstance(admin_data, dict) and "Admin" in admin_data:
        for admin in admin_data["Admin"]:
            if isinstance(admin, dict) and "member_id" in admin and admin["member_id"] == token:
                existing_logins = load_data("member.json")
            if not isinstance(existing_logins, list):
                    existing_logins = []
           
            # Append the new login data
            
            new_member_data = {
                    "name": newuser.name,
                    "role": newuser.role,
                    "password": newuser.password,  
                    "member_id": str(uuid.uuid4())
                }
            existing_logins.append(new_member_data)


            save_data("member.json", existing_logins)

            return {"message": "Member added successfully", "new_member": new_member_data}
    
    raise HTTPException(status_code=403, detail="Forbidden: Invalid token, only admins can add members.")

class NewBooks(BaseModel):
    title:str
    author:str
    stock:int
   


@app.post("/add_books")
def add_books(newbook: NewBooks, request: Request):
    print(f"Request Headers: {request.headers}")
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    if not auth_header or "Bearer " not in auth_header:
        print("No token received or incorrect token")
        raise HTTPException(status_code=401, detail="Unauthorized: Missing or invalid token")
    
    token = auth_header.replace("Bearer ", "").strip()
    print(f"Received token: {token}")
    
    admin_data = load_data("admin.json")
    if isinstance(admin_data, dict) and "Admin" in admin_data:
        for admin in admin_data["Admin"]:
            if isinstance(admin, dict) and "member_id" in admin and admin["member_id"] == token:
                existing_logs = load_data("books.json")
                if not isinstance(existing_logs, list):
                    existing_logs = []
                
                new_books_data = {
                    "title": newbook.title,
                    "author": newbook.author,
                    "stock": newbook.stock,
                    "book_id": str(uuid.uuid4())
                }
                existing_logs.append(new_books_data)
                save_data("books.json", existing_logs)
                return {"message": "Book added successfully","new_book":new_books_data}
    
    raise HTTPException(status_code=403, detail="Forbidden: Invalid token, only admins can add books")


                
                
                
            
            

    
    
    
    
