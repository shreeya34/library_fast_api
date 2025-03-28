from pydantic import BaseModel
from typing import List


    
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
    

class BorrowRequest(BaseModel):
    title: str
    
class ReturnBookRequest(BaseModel):
    title: str