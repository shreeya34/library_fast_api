from datetime import datetime
from pydantic import BaseModel
from typing import List


# admin
class MemberResponse(BaseModel):
    name: str
    role: str
    member_id: str


class MembersListResponse(BaseModel):
    filtered_members: List[MemberResponse]


# member
class BorrowedBookResponse(BaseModel):
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime


class ReturnedBookResponse(BaseModel):
    title: str
    member_id: str
    name: str
    borrow_date: datetime
    expiry_date: datetime
