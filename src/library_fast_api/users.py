
from datetime import datetime, timedelta
import logging
import uuid
from argon2 import verify_password
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from handlers.exception_handlers import app
from handlers.exception_handlers.exception_handler import AdminAlreadyExistsError, BookNotFoundError, BookUnavailableError, InvalidAdminCredentialsError, InvalidMemberCredentialsError, MemberAlreadyExistsError, MemberNotFoundError
from library_fast_api.models import Admin, AdminLogin, Book, BookAvailability, BorrowedBooks, Member, MemberLogins, ReturnBook, User,ViewMembers
from library_fast_api.schema import AdminLogins, BorrowBookRequest, BorrowedBookResponse, CreateModel, LoginSchema, MemberLogin, MembersListResponse, NewBooks, NewMember, ReturnBookRequest
from database.sql import get_db
from library_fast_api.schema import MemberResponse
from passwordhasing.password_hasing import hash_password,check_password
from auth.auth_handler import  get_current_user, signJWT
from library_fast_api.logger import logger
# from handlers.exception_handlers.app import register_middleware

# register_middleware(app)

logger = logging.getLogger(__name__)


def add_admin(user: CreateModel, db: Session) -> bool:
    existing_admin = db.query(Admin).filter(Admin.name == user.name).first()
    if existing_admin:
        logger.warning("Attempt to create an admin that already exists: %s", user.name)
        raise AdminAlreadyExistsError(user.name)

    admin_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)

    new_admin = Admin(admin_id=admin_id, name=user.name, password=hashed_password, role="admin")
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    logger.info("New admin added: %s", user.name)
    
    return new_admin

def get_admins(login: AdminLogins, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.name == login.name).first()
    if not admin or not check_password(login.password, admin.password):
        logger.warning("Failed admin login attempt: %s", login.name)
        raise InvalidAdminCredentialsError(login.name)

    access_token = signJWT(admin.name, admin.admin_id)
    
    new_login = AdminLogin(
        name=login.name,
        status="success",
        login_time=datetime.utcnow(),
        password=login.password,
        member_id=admin.admin_id
    )
    db.add(new_login)
    db.commit()
    db.refresh(new_login)
    
    logger.info("Admin logged in: %s", login.name)
    return {"message": "Login successful", "token": access_token, "admin_id": admin.admin_id}


def login_data(logins: LoginSchema, db: Session = Depends(get_db)):
    try:
        user = db.query(Admin).filter(Admin.name == logins.name).first()
    
        if not user or not check_password(logins.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user:
            role='admin'
        else:
            user = db.query(Member).filter(Member.name == logins.name).first()
    
            if not user or not check_password(logins.password, user.password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            role='member'

        access_token = signJWT(user.name,user.admin_id,role=role)
        
        print(f"User role: {user.role}")  

        # if user.role == 'admin':
        #     login_entry = AdminLogin
        # elif user.role == 'member':
        #     login_entry = MemberLogins
        # else:
        #     raise HTTPException(status_code=400, detail="Invalid role")

        # new_login = login_entry(
        #     name=logins.name, 
        #     status="success", 
        #     login_time=datetime.utcnow(),
        #     member_id=user.admin_id, 
        #     password=user.password 
        # )


        # db.add(new_login)
        # db.commit()
        # db.refresh(new_login)

        return {
            "message": "Login successful",
            "token": access_token['access_token'],
            "id": user.id,
            "role": user.role  
        }
    
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())  
        raise HTTPException(status_code=500, detail="An internal error occurred.")


def get_current_users(request: Request, db: Session):
    user_id = request.headers.get("user_id")  
    
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    
    if not admin:  
        raise HTTPException(status_code=403, detail="Only admins can add books")

    return admin  

def add_user_books(
    request: Request, newbook: NewBooks, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_users)
):
    logger.info(f"Admin {current_user.username} is attempting to add/update a book: {newbook.title} by {newbook.author}")

    existing_logs = db.query(Book).filter(
        Book.title == newbook.title, 
        Book.author == newbook.author
    ).first()
    
    if existing_logs:
        existing_logs.stock += newbook.stock
        existing_logs.available = existing_logs.stock > 0
        
        db.commit()
        
        logger.info(f"Book '{existing_logs.title}' updated successfully by {current_user.name}. New stock: {existing_logs.stock}")
        
        return {
            "message": "Book updated successfully", 
            "new_book": {
                "title": existing_logs.title,
                "author": existing_logs.author,
                "stock": existing_logs.stock,
                "available": existing_logs.available
            }
        }

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
    
    logger.info(f"New book '{new_books_data.title}' added successfully by {current_user.username}. Stock: {new_books_data.stock}")

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
        raise MemberAlreadyExistsError(newuser.name)
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
    
    logger.info(f"New member '{new_member_data.name}' added successfully by {current_user.name}")


    return MemberResponse(
        member_id=new_member_data.member_id,
        name=new_member_data.name,
        role=new_member_data.role
    ).dict()
    
def view_available_books(request: Request, db: Session = Depends(get_db)):
    
        books = db.query(Book).all()  

        if not books:
            logger.warning("No books found in the system.")
            return {"message": "No books found in the system"}

        book_data = []

        for book in books:
            is_available = book.stock > 0

            availability_record = db.query(BookAvailability).filter(BookAvailability.book_id == book.id).first()

            if availability_record:
                availability_record.available = is_available
                availability_record.title = book.title
            else:
                new_availability = BookAvailability(book_id=book.id, title=book.title, available=is_available)
                db.add(new_availability)

            book_data.append({"title": book.title, "author": book.author, "available": is_available})

        db.commit()
        logger.info(f"Successfully fetched {len(book_data)} books.")

        return {"message": "Book available", "books": book_data}


def view_all_members(request: Request, db: Session = Depends(get_db)):
    try:
        logger.info("Fetching all members from the database.")
        
        members = db.query(Member).all()

        if not members:
            logger.warning("No members found in the system.")
            return {"message": "No members found in the system"}
        
        for member in members:
            existing_view_member = db.query(ViewMembers).filter(ViewMembers.member_id == member.member_id).first()

            if not existing_view_member:  # Add only if it doesn't exist
                new_view_member = ViewMembers(member_id=member.member_id, name=member.name, role=member.role)
                db.add(new_view_member)

        db.commit()
        
        logger.info(f"Successfully processed {len(members)} members.")

        # Fetch all view members
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
    
        logger.info(f"Login for: {memberLogin.name}")
        
        member = db.query(Member).filter(Member.name == memberLogin.name).first()
        if not member or not check_password(memberLogin.password, member.password):
            logger.warning(f"Invalid login attempt for user: {memberLogin.name}")
            raise InvalidMemberCredentialsError(member.name)

        access_token = signJWT(member.name, member.member_id)
        logger.info(f"Login successful for user: {memberLogin.name}")

        new_login = MemberLogins(
            name=memberLogin.name, 
            status="success", 
            login_time=datetime.utcnow(),
            member_id=member.member_id 
        )
        db.add(new_login)
        db.commit()
        db.refresh(new_login)

        return {"message": "Login successful", "token": access_token, "member_id": member.member_id}
    
    


def get_borrowed_books_data(book_body: BorrowBookRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    book_title = book_body.book_title
    member = db.query(Member).filter(Member.member_id == current_user["user_id"]).first()
    if not member:
        logger.error("Borrow attempt by non-existent member: %s", current_user["user_id"])
        raise MemberNotFoundError(current_user["user_id"])  
    
    book = db.query(Book).filter(Book.title == book_title).first()
    if not book or book.stock <= 0:
        logger.warning("Borrow attempt for unavailable book: %s", book_title)
        raise BookUnavailableError(book_title)  
    
    borrow_date = datetime.now()
    expiry_date = borrow_date + timedelta(weeks=2)
    
    borrowed_book = BorrowedBooks(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        borrow_date=borrow_date,
        expiry_date=expiry_date
    )
    
    book.stock -= 1
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)
    
    logger.info("Book borrowed: %s by %s", book.title, member.name)
    return {
        "message": "Book borrowed successfully",
        "book_title": book.title,
        "borrow_date": borrow_date,
        "expiry_date": expiry_date
    }
   

def get_returned_books_data(book_body: ReturnBookRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    book_title = book_body.book_title
    member = db.query(Member).filter(Member.member_id == current_user["user_id"]).first()
    if not member:
        logger.error("Return attempt by non-existent member: %s", current_user["user_id"])
        raise MemberNotFoundError(current_user["user_id"])  
    
    book = db.query(Book).filter(Book.title == book_title).first()
    if not book:
        logger.warning("Return attempt for non-existent book: %s", book_title)
        raise BookNotFoundError(book_title)  # Custom exception
    
    return_date = datetime.now()
    borrowed_book = ReturnBook(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        return_date=return_date
    )
    
    book.stock += 1
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)
    
    logger.info("Book returned: %s by %s", book.title, member.name)
    return {
        "message": "Book returned successfully",
        "book_title": book.title,
        "return_date": return_date
    }

