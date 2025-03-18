from pydantic import BaseModel

    
class CreateModel(BaseModel):
    name: str
    password: str
    
class AdminLogin(BaseModel):
    name: str
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

class MembersListResponse(BaseModel):
    filtered_members:list[MemberResponse]

class MemberLogin(BaseModel):
    name: str
    password: str
    

class BorrowRequest(BaseModel):
    name:str
    title: str