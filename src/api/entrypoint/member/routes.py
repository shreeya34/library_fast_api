from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.extension import get_db
from core.auth.auth_bearer import JWTBearer
from core.auth.auth_handler import get_current_user
from api.entrypoint.member.models import (
    MemberLogin,
    BorrowBookRequest,
    ReturnBookRequest,
)
from api.entrypoint.member.responses import BorrowedBookResponse
from modules.user.handlers import (
    member_logins,
    get_borrowed_books_data,
    get_returned_books_data,
)
from api.utils.logger import get_logger

logger = get_logger()


router = APIRouter()


@router.post("/member/login")
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


@router.post(
    "/borrow", response_model=BorrowedBookResponse, dependencies=[Depends(JWTBearer())]
)
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
