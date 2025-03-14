import json
from admin import Admin
from data_handling import load_data, save_data
from fastapi import FastAPI
from pydantic import BaseModel


class AdminLogin(BaseModel):
    name: str
    password: str
    
app = FastAPI()

@app.post("/login")
def login_admin(login: AdminLogin):
    file_name = "admin.json"
    data = load_data(file_name)
    
    print(f"Login Data: {login}") 

    admin_users = data["Admin"]
    
    for user in admin_users:
        if isinstance(user, dict) and login.name == user.get("name") and login.password == user.get("password"):
            login_data = {"name": login.name, "status": "success"}
            save_data("login.json", login_data)
            
            return {"message": "Login Success"}    
    
    return {"message": "Invalid credentials"}
