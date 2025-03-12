from models import Member
from fastapi import FastAPI
from data_handling import load_data
import uuid

app = FastAPI()

class Admin(Member):
    def __init__(self, admin_id, name):
        super().__init__(admin_id, name, "Admin") 
        
@app.post("/admin/")
def create_admin(name:str):
    admin_id = str(uuid.uuid4())
    return {"admin_id":admin_id,"name":name}

@app.get("/admin/")
def get_admins():
    admins = load_admin_data()
    return admins
    
def load_admin_data():
    data = load_data()
    return data.get("Admin",[])



      
