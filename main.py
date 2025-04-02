import json
from argon2 import PasswordHasher
from fastapi.responses import JSONResponse
# from database import Admin
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user
from data_handling import load_data, save_data
from fastapi import Depends, FastAPI, HTTPException, Query, Request
import uuid 
from datetime import datetime, timedelta
from schema import   BorrowBookRequest, CreateModel,AdminLogins, MembersListResponse,NewMember,NewBooks,MemberLogin, MemberResponse, ReturnBookRequest
from sqlalchemy.orm import Session
from sql import get_db,init_db
from models import Admin,AdminLogin,Book, BookAvailability, BorrowedBooks, Member, MemberLogins, ReturnBook
from handlers.users import add_admin,get_admins, add_user_books, get_borrowed_books_data, get_member, get_returned_books_data, member_logins, view_all_members, view_avilable_books
from handlers.exception_handlers import app
from auth.auth_utils import get_token_from_request
from handlers.exception_handlers.app import register_middleware
from handlers.users import get_current_users


app = FastAPI()

register_middleware(app)


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
def login_admin(logins: AdminLogins, db: Session = Depends(get_db))-> dict:
    """
    Login an admin user
    
    **Parameters**:
    - **login**: Admin login details including name and password
    
    **Returns**:
    - A success message with admin ID if login is successful
    - An error message if credentials are incorrect
    """

    login_admin=get_admins(logins, db)
    if login_admin:
        return JSONResponse(status_code=200, content={"message": "Login Success", "admin_id": login_admin["admin_id"],"token": login_admin["token"],})
    else:
        return {"error": "Invalid credentials"}        
    
    
@app.post("/add_member" , dependencies=[Depends(JWTBearer())], tags=["add_member"])
def add_member(request:Request,newuser: NewMember,  db: Session = Depends(get_db))-> dict:
    
    """
    Add a new member to the library system
    
    This endpoint allows an admin to add new member by providing their name, role, and password
    
    **Parameters**:
    - **newuser**: New member details including name, role, and password
    -request: HTTP request containing the admin token
    
    """

   
    members=get_member(request, newuser, db)
    if members:
        return JSONResponse(status_code=201, content={"message": "Member added successfully", "new_member": members})


   
@app.post("/add_books", dependencies=[Depends(JWTBearer())], tags=["add_books"])
def add_books(request:Request,newbook: NewBooks, db: Session = Depends(get_db))-> dict:
    """
    Add or update a book in the system.

    This endpoint allows an admin to add a new book or update the stock of an existing book 
    by providing the title, author, and stock.

    **Parameters**:
    - **newbook**: New book details including title, author, and stock
    - request: HTTP request containing the admin token
    """
    # admin_token = token(request, db)
   
    result = add_user_books(request, newbook, db)
    
    # Check if the book exists and was updated
    if 'new_book' in result:
        return JSONResponse(status_code=201, content=result) 

    

@app.get("/view_available_books", dependencies=[Depends(JWTBearer())], tags=["view_books"])
def view_books(request: Request, db: Session = Depends(get_db)):
    """
    View available books in the library
    
    This endpoint allows an admin to view all available books in the library.
    
    **Parameters**:
    - request: HTTP request containing the admin token
    
    **Returns**:
    - A list of books that are available (in stock)
    
    """
   
    viewBooks= view_avilable_books(request, db)
    
    if viewBooks:
        return JSONResponse(status_code=200, content=viewBooks)
 

@app.get("/view_members", response_model=MembersListResponse, dependencies=[Depends(JWTBearer())], tags=["view_members"])
def view_members(request: Request, db: Session = Depends(get_db)):
    """
    View all members
    
    This endpoint allows an admin to view a list of all members.
    
    **Parameters**:
    - request: HTTP request containing the admin token
    
    **Returns**:
    - A list of members 
    """
    
    return view_all_members(request,db)
   

@app.post("/member/login")
def members(memberLogin: MemberLogin ,db: Session = Depends(get_db))-> dict:
    """
    Login for a member
    
    This endpoints checks the provided credentials and return the member's login status.
    
    **Parameters**:
    -memberLogin: Member login details including name and password
    
    **Returns**:
    -Asucess message if the login is successful
    -An error message if the credentials are incorrect
    
    """
    login_member=member_logins(memberLogin, db)
    if login_member:
        return JSONResponse(status_code=200, content={"message": "Login Success", "admin_id": login_member["member_id"],"token": login_member["token"],})
    else:
        return {"error": "Invalid credentials"}        
    

def member_token(request: Request):
    """
    Validate the member token
    
    **Paremeters**:
    -request: HTTP request containing the member token
    
    **Returns**:
    -A success message if the token is valid
    -An error message if the token is invalid

    """
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



@app.post("/borrow/", dependencies=[Depends(JWTBearer())])
def borrow_book(
    book_body: BorrowBookRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    
    borrowed_books = get_borrowed_books_data(book_body,current_user,db)
    if borrowed_books:
        return JSONResponse(status_code=201, content={"message": "Book borrowed successfully", "borrowed_books": borrowed_books})
    else:
        raise HTTPException(status_code=400,detail="Unable to borrow books,please check it")
        

     
@app.post("/member/return_book", dependencies=[Depends(JWTBearer())])
def return_books( book_body: ReturnBookRequest,current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    """
    Return a book
    
    This endpoint allows a member to return a book to the library
    
    **Parameters**:
    -request: Borrow request including the name of the member and the title of the book
    -requests: HTTP request containing the member token
    
    **Returns**:
    -A success message if the book is returned successfully
    -An error message if the book is not borrowed or the member is not found
    """

    returned_books = get_returned_books_data(book_body,current_user,db)
    if returned_books:
        return JSONResponse(status_code=201, content={"message": "Book returned successfully", "returned_books": returned_books})
    else:
        raise HTTPException(status_code=400,detail="Unable to return books,please check it")
        