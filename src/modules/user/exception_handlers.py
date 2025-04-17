from fastapi import HTTPException


class AdminAccessDeniedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")


class RaiseUnauthorizedError(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = f"User not authenticated"
        super().__init__(status_code=self.status_code, detail=self.detail)


class RaiseBookError(HTTPException):
    def __init__(self, detail: str):
        self.status_code = 400
        self.detail = f"Unable to return the book"
        super().__init__(status_code=self.status_code, detail=self.detail)


class RaiseBorrowBookError(HTTPException):
    def __init__(self, detail: str):
        self.status_code = 400
        self.detail = f"Unable to borrow the book"
        super().__init__(status_code=self.status_code, detail=self.detail)

class DuplicateBookBorrowError(HTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=400,
            detail=f"Book '{book_title}' has already been borrowed by you."
        )
        
class BookNotBorrowedError(Exception):
    def __init__(self, book_title: str):
        self.book_title = book_title
        self.message = f"The book '{self.book_title}' was not borrowed by the member."
        super().__init__(self.message)
