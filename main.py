import json
from argon2 import PasswordHasher
from fastapi.responses import JSONResponse
# from database import Admin
from data_handling import load_data, save_data
from fastapi import Depends, FastAPI, HTTPException, Request
import uuid 
from datetime import datetime, timedelta
from schema import CreateModel,AdminLogins, MembersListResponse,NewMember,NewBooks,MemberLogin,BorrowRequest, MemberResponse
from sqlalchemy.orm import Session
from sql import get_db,init_db
from models import Admin,AdminLogin,Book, Member
from handlers.users import add_admin, get_admins, get_books, get_member, view_all_members, view_avilable_books
from handlers.exception_handlers import app

app = FastAPI()

init_db()



def token(request: Request, db: Session = Depends(get_db)):
    print(f"Request Headers: {request.headers}")
    
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    if not auth_header or "Bearer " not in auth_header:
        raise HTTPException(status_code=401, detail="No token received or incorrect format!")

    token = auth_header.replace("Bearer ", "").strip()
    print(f"Received token: {token}")
    
    # Query the AdminLogin model using the db session
    admin = db.query(AdminLogin).filter(AdminLogin.member_id == token).first()
    
    if admin:
        return True  # Token valid
    
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/admin/")
def create_admin(user: CreateModel, db: Session = Depends(get_db))-> dict:
    """
    Create a new admin user
    
    - **user**: Admin user details including name and password
    
    Returns the admin ID and name of the created admin
    
    - **return**: A dictionary containing the admin ID and name
    """

    
    sucess = add_admin(user, db)
    if sucess:
        return JSONResponse(status_code=201, content={"id": sucess.admin_id, "name": sucess.name})

@app.post("/login")
def login_admin(login: AdminLogins, db: Session = Depends(get_db))-> dict:
    """
    Login an admin user
    
    **Parameters**:
    - **login**: Admin login details including name and password
    
    **Returns**:
    - A success message with admin ID if login is successful
    - An error message if credentials are incorrect
    """

    login_admin=get_admins(login, db)
    if login_admin:
        return JSONResponse(status_code=200, content={"message": "Login Success", "admin_id": login_admin.member_id})
        
    
    
@app.post("/add_member")
def add_member(request:Request,newuser: NewMember,  db: Session = Depends(get_db))-> dict:
    
    """
    Add a new member to the library system
    
    This endpoint allows an admin to add new member by providing their name, role, and password
    
    **Parameters**:
    - **newuser**: New member details including name, role, and password
    -request: HTTP request containing the admin token
    
    """
    admin_token = token(request,db)  
    if not admin_token:
        return {"error": "Invalid admin token"}
    members=get_member(request, newuser, db)
    if members:
        return JSONResponse(status_code=201, content={"message": "Member added successfully", "new_member": members})


   
@app.post("/add_books")
def add_books(request:Request,newbook: NewBooks, db: Session = Depends(get_db))-> dict:
    """
    Add or update a book in the system.

    This endpoint allows an admin to add a new book or update the stock of an existing book 
    by providing the title, author, and stock.

    **Parameters**:
    - **newbook**: New book details including title, author, and stock
    - request: HTTP request containing the admin token
    """
    admin_token = token(request, db)
    
    result = get_books(request, newbook, db)
    
    # Check if the book exists and was updated
    if 'new_book' in result:
        return JSONResponse(status_code=201, content=result) 

    

@app.get("/view_available_books")
def view_books(request: Request, db: Session = Depends(get_db)):
    """
    View available books in the library
    
    This endpoint allows an admin to view all available books in the library.
    
    **Parameters**:
    - request: HTTP request containing the admin token
    
    **Returns**:
    - A list of books that are available (in stock)
    
    """
    admin_token = token(request,db)  
    viewBooks= view_avilable_books(request, db)
    
    if viewBooks:
        return JSONResponse(status_code=200, content=viewBooks)
 

@app.get("/view_members", response_model=MembersListResponse)
async def view_members(request: Request, db: Session = Depends(get_db)):
    """
    View all members
    
    This endpoint allows an admin to view a list of all members.
    
    **Parameters**:
    - request: HTTP request containing the admin token
    
    **Returns**:
    - A list of members 
    """
    admin_token = token(request)  
    
    members = view_all_members()



# @app.post("/member/login")
# def members(memberLogin: MemberLogin):
#     """
#     Login for a member
    
#     This endpoints checks the provided credentials and return the member's login status.
    
#     **Parameters**:
#     -memberLogin: Member login details including name and password
    
#     **Returns**:
#     -Asucess message if the login is successful
#     -An error message if the credentials are incorrect
    
#     """
    
#     file_name = "member.json"
#     data = load_data(file_name)
#     if not isinstance(data, list):
#         raise HTTPException(status_code=500, detail="Invalid member data format")
    
#     for user in data:
#         if isinstance(user, dict) and memberLogin.name == user.get("name") and memberLogin.password == user.get("password"):
#             member_login = {"name": memberLogin.name, "status": "success", "member_id": user.get("member_id")}
            
#             existing_logins = load_data("member_login.json")
#             if not isinstance(existing_logins, list):
#                 existing_logins = []
   
#             existing_logins.append(member_login)
#             save_data("member_login.json", existing_logins)
            
#             return {"message": "Login Success", "member_id": user.get("member_id")}
    
#     return {"message": "Invalid credentials"}

# def member_token(request: Request):
#     """
#     Validate the member token
    
#     **Paremeters**:
#     -request: HTTP request containing the member token
    
#     **Returns**:
#     -A success message if the token is valid
#     -An error message if the token is invalid

#     """
#     print(f"Request Headers: {request.headers}")
    
#     auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

#     if not auth_header or "Bearer " not in auth_header:
#         raise HTTPException(status_code=401, detail="No token received or incorrect format!")

#     token = auth_header.replace("Bearer ", "").strip()
#     print(f"Received token: {token}")

#     member_data = load_data("member.json")
    
#     if isinstance(member_data, list):
#         for member in member_data: 
#             if isinstance(member, dict) and "member_id" in member and member["member_id"] == token:
#                 return {"message":"hello"} 
#     raise HTTPException(status_code=403, detail="Invalid token")


# @app.post("/member/borrow_books")
# def borrow_books(request: BorrowRequest, requests: Request):
#     """
#     Borrow a book
    
#     This endpoint allows a member to borrow a book from the library
    
#     **Parameters**:
#     -request: Borrow request including the name of the member and the title of the book
#     -requests: HTTP request containing the member token
    
#     **Returns**:
#     -A success message if the book is borrowed successfully
#     -An error message if the book is not available or the member is not found
    
#     """
#     token = member_token(requests)
#     try:
#         members_data = load_data("member.json")
#         if not isinstance(members_data, list):
#             raise HTTPException(status_code=500, detail="Invalid member data format")
        
#         member = next((member for member in members_data if member.get("name") == request.name), None)
#         if not member:
#             raise HTTPException(status_code=404, detail="Member not found")

#         books_data = load_data("books.json")
#         if not isinstance(books_data, list):
#             raise HTTPException("Invalid books data format")
        
#         book = next((book for book in books_data if book.get("title") == request.title), None)
#         if not book:
#             raise HTTPException("Book not found")
        
#         stock = int(book.get("stock", 0))
#         if stock <= 0:
#             raise HTTPException("Book is out of stock")
        
#         book["stock"] = stock - 1  
#         save_data("books.json", books_data)
        
#         borrow_log = {
#             "name": request.name,
#             "title": request.title,
#             "borrow_date": datetime.now().strftime("%Y-%m-%d"),
#             "expiry_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")  # 15-day return period
#         }
        
#         borrow_logs = load_data("borrow_logs.json")
#         if not isinstance(borrow_logs, list):
#             borrow_logs = []
#         borrow_logs.append(borrow_log)
#         save_data("borrow_logs.json", borrow_logs)
#         return {"message": "Book borrowed successfully", "borrow_log": borrow_log}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
# @app.post("/member/return_book")
# def return_books(request: BorrowRequest, requests: Request):
#     """
#     Return a book
    
#     This endpoint allows a member to return a book to the library
    
#     **Parameters**:
#     -request: Borrow request including the name of the member and the title of the book
#     -requests: HTTP request containing the member token
    
#     **Returns**:
#     -A success message if the book is returned successfully
#     -An error message if the book is not borrowed or the member is not found
#     """
#     tokens = member_token(requests)
#     try:
#         members_data = load_data("member.json")
#         if not isinstance(members_data, list):
#             raise HTTPException(status_code=500, detail="Invalid member data format")
        
#         member = next((members for members_return in members_data if members_return.get("name" ) == request.name), None)
#         if not member:
#             raise HTTPException(status_code=404, detail="Member not found")
        
#         borrow_logs = load_data("borrow_logs.json")
#         if not isinstance(borrow_logs, list):
#             borrow_logs = []

#         borrowed_book = next(
#             (log for log in borrow_logs if log.get("name") == request.name and log.get("title") == request.title),
#             None
#         )
#         if not borrowed_book:
#             raise HTTPException(status_code=400, detail="You did not borrow this book")

#         books_data = load_data("books.json")
#         if not isinstance(books_data, list):
#             raise HTTPException("Invalid books data format")
        
#         book = next((book for book in books_data if book.get("title") == request.title), None)
       
#         stock = int(book.get("stock", 0))
#         book["stock"] = stock + 1  
#         save_data("books.json", books_data)
        
#         return_log = {
#             "name": request.name,
#             "title": request.title,
#             "return_date": datetime.now().strftime("%Y-%m-%d"),
#         }
#         borrow_logs = load_data("return_logs.json")
#         if not isinstance(borrow_logs, list):
#             borrow_logs = []
#         borrow_logs.append(return_log)
#         save_data("return_logs.json", borrow_logs)
        
#         return {"message": "Book return successfully", "return_log": return_log}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    