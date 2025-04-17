from fastapi import HTTPException
from typing import List


class AdminAlreadyExistsError(HTTPException):
    def __init__(self, name: str):
        self.status_code = 400
        self.detail = f"Admin with the name '{name}' already exists!"
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidAdminCredentialsError(HTTPException):
    def __init__(self, name: str):
        self.status_code = 401
        self.detail = f"Invalid credentials for admin '{name}'"
        super().__init__(status_code=self.status_code, detail=self.detail)


class MemberAlreadyExistsError(HTTPException):
    def __init__(self, name: str):
        self.status_code = 400
        self.detail = f"Member with the name '{name}' already exists!"
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidMemberCredentialsError(HTTPException):
    def __init__(self, name: str):
        self.status_code = 401
        self.detail = f"Invalid credentials for member '{name}'"
        super().__init__(status_code=self.status_code, detail=self.detail)


class MemberNotFoundError(HTTPException):
    def __init__(self, member_id: str):
        self.status_code = 400
        self.detail = f"Member with ID '{member_id}' not found!"
        super().__init__(status_code=self.status_code, detail=self.detail)


class BookUnavailableError(HTTPException):
    def __init__(self, title: str):
        self.status_code = 404
        self.detail = f"Book with title '{title}' is currently unavailable!"
        super().__init__(status_code=self.status_code, detail=self.detail)


class BookNotFoundError(HTTPException):
    def __init__(self, title: str):
        self.status_code = 404
        self.detail = f"Book with title '{title}' not found!"
        super().__init__(status_code=self.status_code, detail=self.detail)


class AdminAccessDeniedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")


class RaiseUnauthorizedError(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = f"User not authenticated"
        super().__init__(status_code=self.status_code, detail=self.detail)
