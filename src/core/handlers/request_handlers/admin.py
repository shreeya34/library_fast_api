from datetime import datetime
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.handlers.exception_handlers.exception_handler import (
    AdminAlreadyExistsError,
    InvalidAdminCredentialsError,
    MemberAlreadyExistsError,
)
from models.db_admin import (
    Admin,
    AdminLogin,
    Book,
    BookAvailability,
    Member,
    ViewMembers,
)
from api.entrypoint.admin.models import (
    AdminLogins,
    CreateModel,
    NewBooks,
    NewMember,
)
from database.sql import get_db
from api.entrypoint.admin.responses import MemberResponse
from core.auth.helpers.password_hasing import generate_random_password, hash_password, check_password
from core.auth.auth_handler import signJWT
from library_fast_api.logger import logger
from api.entrypoint.admin.responses import MembersListResponse
from library_fast_api.logger.logger import get_logger
from core.auth.auth_handler import get_current_user


logger = get_logger()


def add_admin(admin: CreateModel, db: Session) -> bool:
    existing_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if existing_admin:
        logger.warning(
            "Attempt to create an admin that already exists: %s", admin.username
        )
        raise AdminAlreadyExistsError(admin.username)

    admin_id = str(uuid.uuid4())
    hashed_password = hash_password(admin.password)

    new_admin = Admin(
        admin_id=admin_id,
        username=admin.username,
        password=hashed_password,
        role="admin",
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    new_member = Member(
        member_id=admin_id,
        name=admin.username,
        password=hashed_password,
        role="admin",
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    logger.info("New admin and member added: %s", admin.username)

    return new_admin

   


def get_admins(admin_data: AdminLogins, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == admin_data.username).first()
    if not admin or not check_password(admin_data.password, admin.password):
        logger.warning("Failed admin login attempt: %s", admin_data.username)
        raise InvalidAdminCredentialsError(admin_data.username)

    access_token = signJWT(admin.username, admin.admin_id, is_admin=True)

    new_login = AdminLogin(
        username=admin_data.username,
        status="success",
        login_time=datetime.utcnow(),
        password=admin_data.password,
        member_id=admin.admin_id,
    )
    db.add(new_login)
    db.commit()
    db.refresh(new_login)

    logger.info("Admin logged in: %s", admin_data.username)
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

        return {
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
    
    plain_password = generate_random_password()

    hashed_password = hash_password(plain_password)

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
        password=plain_password, 
    ).dict()


def view_available_books(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):

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
