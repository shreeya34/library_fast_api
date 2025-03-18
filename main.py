import json
from argon2 import PasswordHasher
from database import Admin
from data_handling import load_data, save_data
from fastapi import Depends, FastAPI, HTTPException, Request
import uuid 
from datetime import datetime, timedelta
from models import CreateModel,AdminLogin, MembersListResponse,NewMember,NewBooks,MemberLogin,BorrowRequest, MemberResponse


app = FastAPI()

def token(request: Request):
    print(f"Request Headers: {request.headers}")
    
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    if not auth_header or "Bearer " not in auth_header:
        raise HTTPException(status_code=401, detail="No token received or incorrect format!")

    token = auth_header.replace("Bearer ", "").strip()
    print(f"Received token: {token}")

    admin_data = load_data("admin.json")
    
    if isinstance(admin_data, dict) and "Admin" in admin_data:
        for admin in admin_data["Admin"]:
            if isinstance(admin, dict) and "member_id" in admin and admin["member_id"] == token:
                return True  # Authorization successful
    
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/admin/")
def create_admin(user: CreateModel):
    file_name = "admin.json"
    data = load_data(file_name)
    if isinstance(data, list):
        data = {"Admin": data} 
    admin_id = str(uuid.uuid4())
    print(user.name)
    # password = PasswordHasher()
    # hashed_password = password.hash(user.password.encode('utf-8')) 
    admin = Admin(admin_id=admin_id, name=user.name, password=user.password)
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

    
@app.post("/add_member")
def add_member(newuser: NewMember, request: Request,token: bool = Depends(token)):
    existing_logins = load_data("member.json")
    if not isinstance(existing_logins, list):
        existing_logins = []

    new_member_data = {
        "name": newuser.name,
        "role": newuser.role,
        "password": newuser.password,  
        "member_id": str(uuid.uuid4())
    }
    
    existing_logins.append(new_member_data)
    save_data("member.json", existing_logins)

    return {"message": "Member added successfully", "new_member": new_member_data}

   
@app.post("/add_books")
def add_books(newbook: NewBooks, request: Request,token: bool = Depends(token)):
                existing_logs = load_data("books.json")
                if not isinstance(existing_logs, list):
                    existing_logs = []

                new_books_data = {
                    "title": newbook.title,
                    "author": newbook.author,
                    "stock": newbook.stock,
                    "book_id": str(uuid.uuid4())
                }
                for existing_log in existing_logs:
                    if (
                        new_books_data["title"] == existing_log["title"] 
                        and new_books_data["author"] == existing_log["author"]
                        ):
                        existing_log["stock"] = existing_log["stock"] + new_books_data["stock"]
                        save_data("books.json", existing_logs)
                        return {"message": "Book updated successfully","new_book":new_books_data}
                        
                existing_logs.append(new_books_data)
                save_data("books.json", existing_logs)
                return {"message": "Book added successfully","new_book":new_books_data}
    

@app.get("/view_avilable_books")
def view_books():
    try:
        books_data = load_data("books.json")
        if not isinstance(books_data, list):
            books_data = []

        available_books = [book for book in books_data if int(book.get("stock", 0)) > 0]

        for book in available_books:
            stock = int(book.get("stock", 0))
            print(f"{book['title']} by {book['author']} (Stock: {stock})")
                
        return {"message": "Available books", "books": available_books}
    except:
        raise HTTPException(status_code=500, detail="An error occurred while fetching books")


@app.get("/view_members", response_model=MembersListResponse)
async def view_members():
    try:
        member_data = load_data("member.json")
        if not isinstance(member_data, list):
            member_data = []

        # filtered_members = [{"name": member.get("name"), "role": member.get("role"),} for member in member_data]
        filtered_members = [MemberResponse(**member) for member in member_data]
        

        return MembersListResponse(filtered_members=filtered_members)
    except Exception as err:
        raise HTTPException(status_code=500, detail="An error occurred while fetching members")


def member_token(request: Request):
    print(f"Request Headers: {request.headers}")
    
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    if not auth_header or "Bearer " not in auth_header:
        raise HTTPException(status_code=401, detail="No token received or incorrect format!")

    token = auth_header.replace("Bearer ", "").strip()
    print(f"Received token: {token}")

    member_data = load_data("member.json")
    
    if isinstance(member_data, list):
        for member in member_data: 
            if isinstance(member, dict) and "member_id" in member and member["member_id"] == token:
                return {"message":"hello"} 
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/member/login")
def members(memberLogin: MemberLogin):
    file_name = "member.json"
    data = load_data(file_name)
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid member data format")
    for user in data:
        if isinstance(user, dict) and memberLogin.name == user.get("name") and memberLogin.password == user.get("password"):
            member_login = {"name": memberLogin.name, "status": "success", "member_id": user.get("member_id")}
            
            existing_logins = load_data("member_login.json")
            if not isinstance(existing_logins, list):
                existing_logins = []
   
            existing_logins.append(member_login)
            save_data("member_login.json", existing_logins)
            
            return {"message": "Login Success", "member_id": user.get("member_id")}
    
    return {"message": "Invalid credentials"}


@app.post("/member/borrow_books")
def borrow_books(request: BorrowRequest, requests: Request,token: bool = Depends(member_token)):
    try:
        members_data = load_data("member.json")
        if not isinstance(members_data, list):
            raise HTTPException(status_code=500, detail="Invalid member data format")
        
        # Check if member exists
        member = next((member for member in members_data if member.get("name") == request.name), None)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        books_data = load_data("books.json")
        if not isinstance(books_data, list):
            raise HTTPException("Invalid books data format")
        
        book = next((book for book in books_data if book.get("title") == request.title), None)
        if not book:
            raise HTTPException("Book not found")
        
        stock = int(book.get("stock", 0))
        if stock <= 0:
            raise HTTPException("Book is out of stock")
        
        book["stock"] = stock - 1  
        save_data("books.json", books_data)
        
        borrow_log = {
            "name": request.name,
            "title": request.title,
            "borrow_date": datetime.now().strftime("%Y-%m-%d"),
            "expiry_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")  # 15-day return period
        }
        
        borrow_logs = load_data("borrow_logs.json")
        if not isinstance(borrow_logs, list):
            borrow_logs = []
        borrow_logs.append(borrow_log)
        save_data("borrow_logs.json", borrow_logs)
        return {"message": "Book borrowed successfully", "borrow_log": borrow_log}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
@app.post("/member/return_book")
def return_books(request: BorrowRequest, requests: Request,token: bool = Depends(member_token)):
    try:
        members_data = load_data("member.json")
        if not isinstance(members_data, list):
            raise HTTPException(status_code=500, detail="Invalid member data format")
        
        member = next((m for m in members_data if m.get("name") == request.name), None)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        books_data = load_data("books.json")
        if not isinstance(books_data, list):
            raise HTTPException("Invalid books data format")
        
        book = next((book for book in books_data if book.get("title") == request.title), None)
       
        stock = int(book.get("stock", 0))
        book["stock"] = stock + 1  
        save_data("books.json", books_data)
        
        return_log = {
            "name": request.name,
            "title": request.title,
            "return_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
    
        borrow_logs = load_data("return_logs.json")
        if not isinstance(borrow_logs, list):
            borrow_logs = []
        borrow_logs.append(return_log)
        save_data("return_logs.json", borrow_logs)
        
        return {"message": "Book return successfully", "return_log": return_log}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
