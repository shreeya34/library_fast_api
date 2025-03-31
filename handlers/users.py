
from datetime import datetime
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import Admin, AdminLogin, Book, BookAvailability, Member, MemberLogins,ViewMembers
from schema import AdminLogins, CreateModel, MemberLogin, MembersListResponse, NewBooks, NewMember
from sql import get_db
from schema import MemberResponse
from password_hasing import hash_password,check_password
# from token_1 import create_access_token
from auth.auth_handler import  signJWT


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

    access_token = signJWT(admin.name)
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

    
def add_user_books(request: Request, newbook: NewBooks, db: Session = Depends(get_db)):
    # Check if the book already exists
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


def get_member(request: Request, newuser: NewMember, db: Session = Depends(get_db)):
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

        access_token = signJWT(member.name)

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




