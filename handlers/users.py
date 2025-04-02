
from datetime import datetime, timedelta
import logging
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import Admin, AdminLogin, Book, BookAvailability, BorrowedBooks, Member, MemberLogins, ReturnBook,ViewMembers
from schema import AdminLogins, BorrowBookRequest, BorrowedBookResponse, CreateModel, LoginSchema, MemberLogin, MembersListResponse, NewBooks, NewMember, ReturnBookRequest
from sql import get_db
from schema import MemberResponse
from password_hasing import hash_password,check_password
# from token_1 import create_access_token
from auth.auth_handler import  get_current_user, signJWT


def add_admin(user: CreateModel, db: Session) -> bool:
    existing_admin = db.query(Admin).filter(Admin.name == user.name).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with the same name already exists!")

    admin_id = str(uuid.uuid4())
    
    # Ensure password hashing is correct
    hashed_password = hash_password(user.password)  

    new_admin = Admin(admin_id=admin_id, name=user.name, password=hashed_password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin

def get_admins(login: AdminLogins, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.name == login.name).first()
    
    if not admin or not check_password(login.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = signJWT(admin.name,admin.admin_id)

    print(access_token)
    if admin:
        member_id = admin.admin_id
        new_login = AdminLogin(
            name=login.name, 
            status="success", 
            login_time=datetime.utcnow(),
            password=login.password,
            member_id=member_id
        )
        db.add(new_login)
        db.commit()
        db.refresh(new_login)

        return {"message": "Login successful", "token": access_token,"admin_id": admin.admin_id}

#  logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
def login(login: LoginSchema, db: Session = Depends(get_db)):
    user = None
    role = None
    try:
        # Check if the user is an Admin
        admin = db.query(Admin).filter(Admin.name == login.name).first()
        if admin:
            user = admin
            role = "admin"

        # Check if the user is a Member
        member = db.query(Member).filter(Member.name == login.name).first()
        if member:
            user = member
            role = "member"

        # If no user found or incorrect password
        if not user or not check_password(login.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = signJWT(member.name,member.member_id)

        
        login_entry = AdminLogin if role == "admin" else MemberLogins

        member_id = user.admin_id if role == "admin" else user.member_id

        # Create new login entry
        new_login = login_entry(
            name=login.name, 
            status="success", 
            login_time=datetime.utcnow(),
            password=login.password,  # Ideally, avoid storing password in the login entry
            member_id=member_id  # Correctly assigning the right member_id based on role
        )

        # Add and commit the login entry to the database
        db.add(new_login)
        db.commit()
        db.refresh(new_login)
        
        # Return successful login response
        return {
            "message": "Login successful",
            "token": access_token,
            "id": member_id,
            "role": role
        }
    
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())  # Capture stack trace for debugging
        raise HTTPException(status_code=500, detail="An internal error occurred.")

def get_current_users(request: Request, db: Session):
    user_id = request.headers.get("user_id")  # Extract user ID from headers
    
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    
    if not admin:  
        raise HTTPException(status_code=403, detail="Only admins can add books")

    return admin  


def add_user_books(request: Request, newbook: NewBooks, db: Session = Depends(get_db),current_user: Admin = Depends(get_current_users)
):

    existing_logs = db.query(Book).filter(
        Book.title == newbook.title, 
        Book.author == newbook.author,
    ).first()
    
    if existing_logs:
        existing_logs.stock += newbook.stock
        if existing_logs.stock > 0:
            existing_logs.available = True
        else:
            existing_logs.available = False
        db.commit()
       
        return {"message": "Book updated successfully", "new_book": {
            "title": existing_logs.title,
            "author": existing_logs.author,
            "stock": existing_logs.stock,
            "available": existing_logs.available
        }}

    new_books_data = Book(
        title=newbook.title,
        author=newbook.author,
        stock=newbook.stock,
        available=True,
        id=str(uuid.uuid4())
    )
    db.add(new_books_data)
    db.commit()
    db.refresh(new_books_data)
    
    # Return newly created book data
    return {
        "message": "Book added successfully",
        "new_book": {
            "title": new_books_data.title,
            "author": new_books_data.author,
            "stock": new_books_data.stock,
            "available": new_books_data.available
        }
    }


def get_member(request: Request, newuser: NewMember, db: Session = Depends(get_db),current_user: Admin = Depends(get_current_users)):
    # Check if a member with the same name already exists
    existing_member = db.query(Member).filter(Member.name == newuser.name).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="Member with this name already exists")
    hashed_password = hash_password(newuser.password)  

    new_member_data = Member(
        name=newuser.name,
        role=newuser.role,
        password=hashed_password,
        member_id=str(uuid.uuid4())
    )

    db.add(new_member_data)
    db.commit()
    db.refresh(new_member_data)

    return MemberResponse(
        member_id=new_member_data.member_id,
        name=new_member_data.name,
        role=new_member_data.role
    ).dict()
    
def view_avilable_books(request:Request,db: Session = Depends(get_db)):
    try:
        books = db.query(Book).all()  

        if not books:
            return {"message": "No books found in the system"}

        book_data = []

        for book in books:
            is_available = book.stock > 0

            availability_record = db.query(BookAvailability).filter(BookAvailability.book_id == book.id).first()

            if availability_record:
                availability_record.available = is_available
                availability_record.title = book.title
            else:
                new_availability = BookAvailability(book_id=book.id, title=book.title,available=is_available)
                db.add(new_availability)

            book_data.append({"title": book.title, "author": book.author, "available": is_available})

        db.commit()

        return {"message": "Book available", "books": book_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
def view_all_members(request: Request, db: Session = Depends(get_db)):
    try:
        members = db.query(Member).all()
        
        for member in members:
            existing_view_member = db.query(ViewMembers).filter(ViewMembers.member_id == member.member_id).first()
        db.add(existing_view_member)
        
        # Commit the changes to the database
        db.commit()

        view_members = db.query(ViewMembers).all()
        member_data = [
            {"name": view_member.name, "role": view_member.role, "member_id": view_member.member_id}
            for view_member in view_members
        ]

        return MembersListResponse(filtered_members=member_data)
    
    except Exception as err:
        print("Error occurred:", str(err))
        raise HTTPException(status_code=500, detail="An error occurred while fetching members")


def member_logins(memberLogin: MemberLogin, db: Session = Depends(get_db)) -> dict:
    
    try:
        member = db.query(Member).filter(Member.name == memberLogin.name).first()
        if not member or not check_password(memberLogin.password, member.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print(f"Login attempt for: {memberLogin.name}")
        print(f"Entered password: {memberLogin.password}")
        print(f"Stored hashed password: {member.password}")

        access_token = signJWT(member.name,member.member_id)

        if member:
            member_id = member.member_id
            new_login = MemberLogins(
                name=memberLogin.name, 
                status="success", 
                login_time=datetime.utcnow(),
                password=memberLogin.password,
                member_id=member_id
            )
            db.add(new_login)
            db.commit()
            db.refresh(new_login)

        return {"message": "Login successful", "token": access_token, "member_id": member.member_id}
    
    except Exception as e:
        print(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


def get_borrowed_books_data(
    book_body: BorrowBookRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    book_title = book_body.book_title
    
    member = db.query(Member).filter(Member.member_id == current_user["user_id"]).first()
    if not member:
        raise HTTPException(status_code=400, detail="Member not found")
    
    book = db.query(Book).filter(Book.title == book_title).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    availability = db.query(BookAvailability).filter(BookAvailability.book_id == book.id).first()
    
    if not availability:
        availability = BookAvailability(book_id=book.id, title=book.title, available=True)
        db.add(availability)
        db.commit()
        db.refresh(availability)
    
    # Now check availability
    if not availability.available:
        raise HTTPException(status_code=400, detail="Book is not available for borrowing")
    
    existing_borrow = db.query(BorrowedBooks).filter(
        BorrowedBooks.member_id == str(member.member_id),  # Ensure matching type
        BorrowedBooks.book_id == book.id
    ).first()
    
    if existing_borrow:
        raise HTTPException(status_code=400, detail="You have already borrowed this book")
    
    if book.stock <= 0:
        raise HTTPException(status_code=400, detail="Book is out of stock")
    
    borrow_date = datetime.now()
    expiry_date = borrow_date + timedelta(weeks=2)
    
    # Create borrow record
    borrowed_book = BorrowedBooks(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        borrow_date=borrow_date,
        expiry_date=expiry_date
    )
    
    book.stock -= 1
    availability.available = book.stock > 0
    
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)
    
    return {
        "message": "Book borrowed successfully",
        "book_title": book.title,
        "borrow_date": borrow_date,
        "expiry_date": expiry_date
    }
   

def get_returned_books_data(
    book_body: ReturnBookRequest,current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)
):
    book_title = book_body.book_title
    member = db.query(Member).filter(Member.member_id == current_user["user_id"]).first()
    if not member:
        raise HTTPException(
            status_code=400,
            detail="Member not found"
        )
    
    # Check if book exists and is available
    book = db.query(Book).filter(Book.title == book_title).first()
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    return_date = datetime.now()
    
    # Create borrowed book record
    borrowed_book = ReturnBook(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        return_date=return_date
    
    )
    
    # Update book availability
    book.stock += 1
   
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)
   
    return {
        "message": "Book returned successfully",
        "book_title": book.title,
        "return_date": return_date
       
    }
