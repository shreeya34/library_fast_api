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
