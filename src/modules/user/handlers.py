from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from api.utils.db_operation import commit_and_refresh
from modules.admin.exception_handler import (
    BookNotFoundError,
    BookUnavailableError,
    InvalidMemberCredentialsError,
    MemberNotFoundError,
    RaiseUnauthorizedError,
)
from db_schema.member import BorrowedBooks, MemberLogins, ReturnBook
from db_schema.admin import Book, Member
from core.handlers.request_handlers.response_handlers import json_response
from api.entrypoint.member.models import (
    BorrowBookRequest,
    MemberLogin,
    ReturnBookRequest,
)
from config.extension import get_db
from core.auth.auth_handler import get_current_user, signJWT
from api.utils.logger import get_logger
from api.entrypoint.member.responses import BorrowedBookResponse
from modules.admin.queries import get_member_by_name
from modules.user.queries import create_member_login, get_book_by_title

logger = get_logger()


def member_logins(memberLogin: MemberLogin, db: Session = Depends(get_db)) -> dict:

    logger.info(f"Login for: {memberLogin.name}")

    member = get_member_by_name(db, memberLogin.name)
    if not member:
        logger.warning(
            "Failed login attempt for non-existent member: %s", memberLogin.name
        )
        raise InvalidMemberCredentialsError(memberLogin.name)

    access_token = signJWT(member.name, member.member_id, is_admin=False)
    logger.info(f"Login successful for user: {memberLogin.name}")

    new_login = create_member_login(db, member.member_id, memberLogin.name)

    return {
        "message": "Login successful",
        "member_id": member.member_id,
        "token": access_token,
    }


def get_borrowed_books_data(
    book_body: BorrowBookRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id")
    if not user_id:
        logger.error("Borrow attempt by user without valid user_id in token")
        raise RaiseUnauthorizedError()

    member = db.query(Member).filter(Member.member_id == user_id).first()
    if not member:
        logger.error("Borrow attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)

    book = get_book_by_title(db, book_title)
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
        borrow_date=borrow_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
    )

    book.stock -= 1
    commit_and_refresh(db, borrowed_book)

    logger.info("Book borrowed: %s by %s", book.title, member.name)
    return BorrowedBookResponse(
        title=book.title,
        member_id=member.member_id,
        name=member.name,
        borrow_date=borrow_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
    )


def get_returned_books_data(
    book_body: ReturnBookRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id")
    if not user_id:
        logger.error("Return attempt by user without valid user_id in token")
        raise RaiseUnauthorizedError()

    member = db.query(Member).filter(Member.member_id == user_id).first()
    if not member:
        logger.error("Return attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)

    book = get_book_by_title(db, book_title)
    if not book:
        logger.warning("Return attempt for non-existent book: %s", book_title)
        raise BookNotFoundError(book_title)
    return_date = datetime.now()
    returned_book = ReturnBook(
        title=book.title,
        member_id=member.member_id,
        book_id=book.id,
        name=member.name,
        return_date=return_date,
    )

    book.stock += 1
    commit_and_refresh(db, returned_book)

    logger.info("Book returned: %s by %s", book.title, member.name)

    return {
        "message": "Book returned successfully",
        "book_title": book.title,
        "name": member.name,
        "return_date": return_date.isoformat(),
    }
