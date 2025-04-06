from datetime import datetime
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from handlers.exception_handlers.exception_handler import (
    AdminAlreadyExistsError,
    InvalidAdminCredentialsError,
    MemberAlreadyExistsError,
    
)
from database.models import (
    Admin,
    AdminLogin,
    Book,
    BookAvailability,
    Member,
    ViewMembers,
)
from handlers.request_handlers.response_handlers import json_response
from models.request_models import (
    AdminLogins,
    CreateModel,
    LoginSchema,
    NewBooks,
    NewMember,
)
from database.sql import get_db
from models.response_models import MemberResponse
from auth.helpers.password_hasing import hash_password, check_password
from auth.auth_handler import signJWT
from library_fast_api.logger import logger
from models.response_models import MembersListResponse
from library_fast_api.logger.logger import get_logger
from auth.auth_handler import get_current_user


logger = get_logger()


def add_admin(user: CreateModel, db: Session) -> bool:
    existing_admin = db.query(Admin).filter(Admin.username == user.username).first()
    if existing_admin:
        logger.warning(
            "Attempt to create an admin that already exists: %s", user.username
        )
        raise AdminAlreadyExistsError(user.username)

    admin_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)

    new_admin = Admin(
        admin_id=admin_id,
        username=user.username,
        password=hashed_password,
        role="admin",
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    # logger.info("New admin added: %s", user.username)
    
    new_member = Member(
        member_id=admin_id,  
        name=user.username,
        password=hashed_password,  
        role="admin",  
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    logger.info("New admin and member added: %s", user.username)

    return new_admin

    return new_admin


def get_admins(login: AdminLogins, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == login.username).first()
    if not admin or not check_password(login.password, admin.password):
        logger.warning("Failed admin login attempt: %s", login.username)
        raise InvalidAdminCredentialsError(login.username)

    access_token = signJWT(admin.username, admin.admin_id, is_admin=True)

    new_login = AdminLogin(
        username=login.username,
        status="success",
        login_time=datetime.utcnow(),
        password=login.password,
        member_id=admin.admin_id,
    )
    db.add(new_login)
    db.commit()
    db.refresh(new_login)

    logger.info("Admin logged in: %s", login.username)
    return {
        "message": "Login successful",
        "token": access_token,
        "admin_id": admin.admin_id,
    }




def add_user_books(
    request: Request,
    newbook: NewBooks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    
    if not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")

    logger.info(
        f"Admin {user['username']} is attempting to add/update a book: {newbook.title} by {newbook.author}"
    )

    existing_logs = (
        db.query(Book)
        .filter(Book.title == newbook.title, Book.author == newbook.author)
        .first()
    )

    if existing_logs:
        existing_logs.stock += newbook.stock
        existing_logs.available = existing_logs.stock > 0

        db.commit()

        logger.info(
            f"Book '{existing_logs.title}' updated successfully by {user['username']}. New stock: {existing_logs.stock}"
        )

        return  {
            "message": "Book updated successfully",
            "new_book": {
                "title": existing_logs.title,
                "author": existing_logs.author,
                "stock": existing_logs.stock,
                "available": existing_logs.available,
            },
        }

    new_books_data = Book(
        title=newbook.title,
        author=newbook.author,
        stock=newbook.stock,
        available=True,
        id=str(uuid.uuid4()),
    )
    db.add(new_books_data)
    db.commit()
    db.refresh(new_books_data)

    logger.info(
        f"New book '{new_books_data.title}' added successfully  Stock: {new_books_data.stock}"
    )

    return {
        "message": "Book added successfully",
        "new_book": {
            "title": new_books_data.title,
            "author": new_books_data.author,
            "stock": new_books_data.stock,
            "available": new_books_data.available,
        },
    }


def get_member(
    request: Request,
    newuser: NewMember,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):  
    
    if not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")

    existing_member = db.query(Member).filter(Member.name == newuser.name).first()

    if existing_member:
        raise MemberAlreadyExistsError(newuser.name)
    hashed_password = hash_password(newuser.password)

    new_member_data = Member(
        name=newuser.name,
        role=newuser.role,
        password=hashed_password,
        member_id=str(uuid.uuid4()),
    )

    db.add(new_member_data)
    db.commit()
    db.refresh(new_member_data)

    logger.info(f"New member '{new_member_data.name}' added successfully")

    return MemberResponse(
        member_id=new_member_data.member_id,
        name=new_member_data.name,
        role=new_member_data.role,
    ).dict()


def view_available_books(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):  # Extract user from JWT

    if not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
    books = db.query(Book).all()

    if not books:
        logger.warning("No books found in the system.")
        return {"message": "No books found in the system"}

    book_data = []

    for book in books:
        is_available = book.stock > 0

        availability_record = (
            db.query(BookAvailability)
            .filter(BookAvailability.book_id == book.id)
            .first()
        )

        if availability_record:
            availability_record.available = is_available
            availability_record.title = book.title
        else:
            new_availability = BookAvailability(
                book_id=book.id, title=book.title, available=is_available
            )
            db.add(new_availability)

        book_data.append(
            {"title": book.title, "author": book.author, "available": is_available}
        )

    db.commit()
    logger.info(f"Successfully fetched {len(book_data)} books.")
    return {"message": "Book available", "books": book_data}



def view_all_members(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
    try:
        logger.info("Fetching all members from the database.")

        members = db.query(Member).all()

        if not members:
            logger.warning("No members found in the system.")
            return {"message": "No members found in the system"}

        for member in members:
            existing_view_member = (
                db.query(ViewMembers)
                .filter(ViewMembers.member_id == member.member_id)
                .first()
            )

            if not existing_view_member:  # Add only if it doesn't exist
                new_view_member = ViewMembers(
                    member_id=member.member_id, name=member.name, role=member.role
                )
                db.add(new_view_member)

        db.commit()

        logger.info(f"Successfully processed {len(members)} members.")

        view_members = db.query(ViewMembers).all()
        member_data = [
            {
                "name": view_member.name,
                "role": view_member.role,
                "member_id": view_member.member_id,
            }
            for view_member in view_members
        ]

        return MembersListResponse(filtered_members=member_data)
    except Exception as err:
        print("Error occurred:", str(err))
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching members"
        )
