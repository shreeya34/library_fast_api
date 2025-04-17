from datetime import datetime
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from api.utils.db_operation import commit_and_refresh
from modules.admin.exception_handler import (
    AdminAccessDeniedError,
    AdminAlreadyExistsError,
    InvalidAdminCredentialsError,
    MemberAlreadyExistsError,
    MemberNotFoundError,
)
from db_schema.admin import (
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
from config.extension import get_db
from api.entrypoint.admin.responses import MemberResponse
from core.auth.security.password_hasing import (
    generate_random_password,
    hash_password,
    check_password,
)
from core.auth.auth_handler import signJWT
from api.utils import logger
from api.entrypoint.admin.responses import MembersListResponse
from api.utils.logger import get_logger
from core.auth.auth_handler import get_current_user
from modules.admin.queries import (
    get_admin_by_username,
    get_all_members,
    get_all_view_members,
    get_book_availability_by_book_id,
    get_existing_book,
    get_member_by_id,
    get_member_by_name,
    get_view_member_by_id,
)


logger = get_logger()


def add_admin(admin: CreateModel, db: Session) -> bool:
    existing_admin = get_admin_by_username(db, admin.username)
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

    commit_and_refresh(db, new_admin)

    new_member = Member(
        member_id=admin_id,
        name=admin.username,
        password=hashed_password,
        role="admin",
    )

    commit_and_refresh(db, new_member)

    logger.info("New admin and member added: %s", admin.username)

    return new_admin


def get_admins(admin_data: AdminLogins, db: Session = Depends(get_db)):
    admin = get_admin_by_username(db, admin_data.username)
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

    commit_and_refresh(db, new_login)

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

    existing_logs = get_existing_book(db, newbook)

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

    commit_and_refresh(db, new_books_data)

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
        raise AdminAccessDeniedError()

    existing_member = get_member_by_name(db, newuser.name)

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

    commit_and_refresh(db, new_member_data)

    logger.info(f"New member '{new_member_data.name}' added successfully")

    return MemberResponse(
        member_id=new_member_data.member_id,
        name=new_member_data.name,
        role=new_member_data.role,
        password=plain_password,
    ).dict()


def view_available_books(
    title: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):

    if not user.get("is_admin"):
        raise AdminAccessDeniedError()
    if title:
        books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    else:
        books = db.query(Book).all()

    
    if not books:
        logger.warning(f"No books found with title '{title}'.")
        return {"message": f"No books found with title '{title}'"}

    book_data = []

    for book in books:
        is_available = book.stock > 0

        availability_record = get_book_availability_by_book_id(db, book.id)

        if availability_record:
            availability_record.available = is_available
            availability_record.title = book.title
        else:
            new_availability = BookAvailability(
                book_id=book.id, title=book.title, available=is_available
            )
            db.add(new_availability)
        if is_available:
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
        raise AdminAccessDeniedError()

    logger.info("Fetching all members from the database.")

    members = get_all_members(db)

    if not members:
        logger.warning("No members found in the system.")
        return {"message": "No members found in the system"}

    for member in members:
        existing_view_member = get_view_member_by_id(db, member.member_id)

        if not existing_view_member:
            new_view_member = ViewMembers(
                member_id=member.member_id, name=member.name, role=member.role
            )
            db.add(new_view_member)

    db.commit()

    logger.info(f"Successfully processed {len(members)} members.")

    view_members = get_all_view_members(db)
    member_data = [
        {
            "name": view_member.name,
            "role": view_member.role,
            "member_id": view_member.member_id,
        }
        for view_member in view_members
    ]

    return MembersListResponse(filtered_members=member_data)


def view_member_by_id(member_id: str, db: Session, user: dict):
    if not user.get("is_admin"):
        raise AdminAccessDeniedError()

    logger.info(f"Fetching member with ID {member_id} from the database.")

    member = get_member_by_id(db, member_id)

    if not member:
        raise MemberNotFoundError(member_id)

    return {
        "name": member.name,
        "role": member.role,
        "member_id": member.member_id,
    }
    
