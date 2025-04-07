from datetime import datetime
from pydantic import BaseModel
from typing import List


class CreateModel(BaseModel):
    username: str
    password: str


class AdminLogins(BaseModel):
    username: str
    status: str
    password: str


class NewMember(BaseModel):
    name: str
    role: str
    password: str


class NewBooks(BaseModel):
    title: str
    author: str
    stock: int


class MemberLogin(BaseModel):
    name: str
    password: str


class ReturnBookRequest(BaseModel):
    book_title: str


class BorrowBookRequest(BaseModel):
    book_title: str
