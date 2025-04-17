from datetime import datetime
from pydantic import BaseModel


class BorrowedBookResponse(BaseModel):
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime
    


class BorrowBookSuccessResponse(BaseModel):
    message: str
    borrowed_book: BorrowedBookResponse


class ReturnedBookResponse(BaseModel):
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime
