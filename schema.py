from datetime import datetime
from pydantic import BaseModel
from typing import List

from sqlalchemy import UUID


    
class CreateModel(BaseModel):
    name: str
    password: str
    
class AdminLogins(BaseModel):
    name: str
    status: str
    password: str
    

    
class NewMember(BaseModel):
    name: str
    role: str
    password: str 


class NewBooks(BaseModel):
    title:str
    author:str
    stock:int

class MemberResponse(BaseModel):
    name: str
    role: str
    member_id: str

class MembersListResponse(BaseModel):
    filtered_members:List[MemberResponse]

class MemberLogin(BaseModel):
    name: str
    password: str
    

    
class ReturnBookRequest(BaseModel):
    book_title: str
    
class LoginSchema(BaseModel):
    name: str
    password: str
class BorrowBookRequest(BaseModel):
    book_title: str
 
class BorrowedBookResponse(BaseModel):
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime
    
    
    
 