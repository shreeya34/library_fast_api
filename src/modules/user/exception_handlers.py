

from fastapi import HTTPException


class AdminAccessDeniedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")
        

class RaiseUnauthorizedError(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = f"User not authenticated"
        super().__init__(status_code=self.status_code, detail=self.detail)