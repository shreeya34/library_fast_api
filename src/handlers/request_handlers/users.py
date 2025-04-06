from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from handlers.exception_handlers import app
from handlers.exception_handlers.exception_handler import (
    BookNotFoundError,
    BookUnavailableError,
    InvalidMemberCredentialsError,
    MemberNotFoundError,
)
from database.models import Book, BorrowedBooks, Member, MemberLogins, ReturnBook
from handlers.request_handlers.response_handlers import json_response
from models.request_models import BorrowBookRequest, MemberLogin, ReturnBookRequest
from database.sql import get_db
from auth.auth_handler import get_current_user, signJWT
from library_fast_api.logger.logger import get_logger

logger = get_logger()


def member_logins(memberLogin: MemberLogin, db: Session = Depends(get_db)) -> dict:

    logger.info(f"Login for: {memberLogin.name}")

    member = db.query(Member).filter(Member.name == memberLogin.name).first()
    if not member:
        logger.warning(
            "Failed login attempt for non-existent member: %s", memberLogin.name
        )
        raise InvalidMemberCredentialsError(memberLogin.name)

    access_token = signJWT(member.name, member.member_id, is_admin=False)
    logger.info(f"Login successful for user: {memberLogin.name}")

    new_login = MemberLogins(
        name=memberLogin.name,
        status="success",
        login_time=datetime.utcnow(),
        member_id=member.member_id,
    )
    db.add(new_login)
    db.commit()
    db.refresh(new_login)

    return {
        "message": "Login successful",
        "member_id": member.member_id,
        "token": access_token,
    }



def get_borrowed_books_data(
    book_body: BorrowBookRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user),

) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id") 
    if not user_id:
        logger.error("Borrow attempt by user without valid user_id in token")
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    member = db.query(Member).filter(Member.member_id == user_id).first()
    if not member:
        logger.error("Borrow attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)
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
        expiry_date=expiry_date,
    )

    book.stock -= 1
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)

    logger.info("Book borrowed: %s by %s", book.title, member.name)
    return {
        "message": "Book borrowed successfully",
        "book_title": book.title,
        "name": member.name,
        "borrow_date": borrow_date.isoformat(),
        "expiry_date": expiry_date.isoformat(),
    }


def get_returned_books_data(
    book_body: ReturnBookRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)

) -> dict:
    book_title = book_body.book_title
    user_id = user.get("admin_id") 
    if not user_id:
        logger.error("Borrow attempt by user without valid user_id in token")
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    member = db.query(Member).filter(Member.member_id == user_id).first()
    if not member:
        logger.error("Borrow attempt by non-existent member: %s", user_id)
        raise MemberNotFoundError(user_id)

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
        return_date=return_date,
    )

    book.stock += 1
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)

    logger.info("Book returned: %s by %s", book.title, member.name)

    return {
        "message": "Book returned successfully",
        "book_title": book.title,
        "name": member.name,
        "return_date": return_date.isoformat(),
    }
