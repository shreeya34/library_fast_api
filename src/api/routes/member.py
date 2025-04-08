from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.sql import get_db
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user
from models.request_models import MemberLogin, BorrowBookRequest, ReturnBookRequest
from models.response_models import BorrowedBookResponse
from handlers.request_handlers.users import (
    member_logins,
    get_borrowed_books_data,
    get_returned_books_data,
)
from library_fast_api.logger.logger import get_logger
logger = get_logger()


router = APIRouter()


@router.post("/login")
def member_login(memberLogin: MemberLogin, db: Session = Depends(get_db)):
    login_member = member_logins(memberLogin, db)
    if login_member:
        return {
            "message": "Login Success",
            "member_id": login_member["member_id"],
            "token": login_member["token"],
        }
    else:
        return {"error": "Invalid credentials"}


@router.post("/borrow", response_model=BorrowedBookResponse, dependencies=[Depends(JWTBearer())])
def borrow_book(
    book_body: BorrowBookRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    borrowed_books = get_borrowed_books_data(book_body, db, user)
    if borrowed_books:
       return borrowed_books  
    else:
        raise HTTPException(status_code=400, detail="Unable to borrow book")


@router.post("/return_book", dependencies=[Depends(JWTBearer())])
def return_books(
    book_body: ReturnBookRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    returned_books = get_returned_books_data(book_body, db, user)
    if returned_books:
        return {
            "message": "Book returned successfully",
            "returned_books": returned_books,
        }
    else:
        raise HTTPException(status_code=400, detail="Unable to return book")
