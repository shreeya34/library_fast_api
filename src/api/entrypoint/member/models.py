from pydantic import BaseModel


class MemberLogin(BaseModel):
    name: str
    password: str


class ReturnBookRequest(BaseModel):
    book_title: str


class BorrowBookRequest(BaseModel):
    book_title: str
