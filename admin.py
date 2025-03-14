from models import Member
from fastapi import FastAPI, HTTPException
from data_handling import load_data, save_data
from pydantic import BaseModel, SecretStr
import uuid

app = FastAPI()

class Admin(Member):
    def __init__(self, admin_id, name, password):
        super().__init__(member_id=admin_id, name=name, role="Admin")
        self.password = password

class CreateModel(BaseModel):
    name: str
    password: SecretStr
    

@app.post("/admin/")
def create_admin(user: CreateModel):
    file_name = "admin.json"
    data = load_data(file_name)
    if isinstance(data, list):
        data = {"Admin": data} 
    admin_id = str(uuid.uuid4())
    print(user.name)
    admin = Admin(admin_id=admin_id, name=user.name, password=user.password.get_secret_value())
    if "Admin" in data:
        data["Admin"].append(admin.__dict__)
    else:
        data["Admin"] = [admin.__dict__]
    
    save_data(file_name, data)
    print(f"Created admin with ID: {admin_id} and name: {admin.name}")
    return {"admin_id": admin_id, "name": admin.name}

@app.get("/admin/")
def get_admins():
    admins = load_admin_data()
    print(f"Loaded admins data: {admins}")
    return admins

def load_admin_data():
    data = load_data()
    print(f"Data loaded: {data}")
    return data.get("Admin", [])
