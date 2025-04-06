import logging
from fastapi.responses import JSONResponse
from auth.auth_bearer import JWTBearer

# from auth.auth_handler import get_current_user
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from auth.auth_handler import get_current_user
from handlers.exception_handlers.exception_handler import InvalidAdminCredentialsError
from handlers.exception_handlers.middleware import ExceptionHandlerMiddleware
from models.request_models import (
    BorrowBookRequest,
    CreateModel,
    AdminLogins,
    LoginSchema,
    NewMember,
    NewBooks,
    MemberLogin,
    ReturnBookRequest,
)
from sqlalchemy.orm import Session
from database.sql import get_db, init_db
from handlers.request_handlers.users import (
    get_borrowed_books_data,
    get_returned_books_data,
    member_logins,
)
from handlers.request_handlers.admin import (
    add_admin,
    get_admins,
    add_user_books,
    get_member,
    view_all_members,
    view_available_books,
)
from models.response_models import MembersListResponse
from library_fast_api.logger.logger import get_logger


logger = get_logger()
app = FastAPI()


init_db()
app.add_middleware(ExceptionHandlerMiddleware)




@app.post("/admin/")
def create_admin(user: CreateModel, db: Session = Depends(get_db)) -> dict:
    """
    Create a new admin user

    - **user**: Admin user details including name and password

    Returns the admin ID and name of the created admin

    - **return**: A dictionary containing the admin ID and name
    """

    logger.info(f"Creating admin: {user.username}")
    sucess = add_admin(user, db)
    if sucess:
        return JSONResponse(
            status_code=201, content={"id": sucess.admin_id, "name": sucess.username}
        )


@app.post("/login")
def login_admin(logins: AdminLogins, db: Session = Depends(get_db)) -> dict:
    """
    Login an admin user

    **Parameters**:
    - **login**: Admin login details including name and password

    **Returns**:
    - A success message with admin ID if login is successful
    - An error message if credentials are incorrect
    """

    try:
        login_result = get_admins(logins, db)
        return {
            "message": "Login Success",
            "admin_id": login_result["admin_id"],
            "token": login_result["token"],
        }
    except InvalidAdminCredentialsError:
        return {"error": "Invalid credentials"}


@app.post("/add_member", dependencies=[Depends(JWTBearer())], tags=["add_member"])
def add_member(
    request: Request, newuser: NewMember, db: Session = Depends(get_db),user: dict = Depends(get_current_user)
) -> dict:
    """
    Add a new member to the library system

    This endpoint allows an admin to add new member by providing their name, role, and password

    **Parameters**:
    - **newuser**: New member details including name, role, and password
    -request: HTTP request containing the admin token

    """

    members = get_member(request, newuser, db,user)
    if members:
        return JSONResponse(
            status_code=201,
            content={"message": "Member added successfully", "new_member": members},
        )


@app.post("/add_books", dependencies=[Depends(JWTBearer())], tags=["add_books"])
def add_books(
    request: Request, newbook: NewBooks, db: Session = Depends(get_db),user: dict = Depends(get_current_user)
) -> dict:
    """
    Add or update a book in the system.

    This endpoint allows an admin to add a new book or update the stock of an existing book
    by providing the title, author, and stock.

    **Parameters**:
    - **newbook**: New book details including title, author, and stock
    - request: HTTP request containing the admin token
    """
    # admin_token = token(request, db)

    result = add_user_books(request, newbook, db,user)

    # Check if the book exists and was updated
    if "new_book" in result:
        return JSONResponse(status_code=201, content=result)


@app.get(
    "/view_available_books", dependencies=[Depends(JWTBearer())], tags=["view_books"]
)
def view_books(request: Request, db: Session = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    View available books in the library

    This endpoint allows an admin to view all available books in the library.

    **Parameters**:
    - request: HTTP request containing the admin token

    **Returns**:
    - A list of books that are available (in stock)

    """

    viewBooks = view_available_books(request, db,user)

    if viewBooks:
        return JSONResponse(status_code=200, content=viewBooks)


@app.get(
    "/view_members",
    response_model=MembersListResponse,
    dependencies=[Depends(JWTBearer())],
    tags=["view_members"]
)
def view_members(request: Request, db: Session = Depends(get_db),user: dict = Depends(get_current_user)):
    """
    View all members

    This endpoint allows an admin to view a list of all members.

    **Parameters**:
    - request: HTTP request containing the admin token

    **Returns**:
    - A list of members
    """

    return view_all_members(request, db,user)


@app.post("/member/login")
def members(memberLogin: MemberLogin, db: Session = Depends(get_db)) -> dict:
    """
    Login for a member

    This endpoints checks the provided credentials and return the member's login status.

    **Parameters**:
    -memberLogin: Member login details including name and password

    **Returns**:
    -Asucess message if the login is successful
    -An error message if the credentials are incorrect

    """
    login_member = member_logins(memberLogin, db)
    if login_member:
        
            content={
                "message": "Login Success",
                "admin_id": login_member["member_id"],
                "token": login_member["token"],
            },
            return JSONResponse(status_code=200, content=content)

        
    else:
        return {"error": "Invalid credentials"}


@app.post("/borrow/", dependencies=[Depends(JWTBearer())])
def borrow_book(
    book_body: BorrowBookRequest,
    # current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),user: dict = Depends(get_current_user)
) -> dict:

    borrowed_books = get_borrowed_books_data(book_body, db,user)
    if borrowed_books:
        
            content={
                "message": "Book borrowed successfully",
                "borrowed_books": borrowed_books,
            },
            return JSONResponse(status_code=200, content=content)

        
    else:
        raise HTTPException(
            status_code=400, detail="Unable to borrow books,please check it"
        )


@app.post("/member/return_book", dependencies=[Depends(JWTBearer())])
def return_books(book_body: ReturnBookRequest, db: Session = Depends(get_db),user: dict = Depends(get_current_user)) -> dict:
    """
    Return a book

    This endpoint allows a member to return a book to the library

    **Parameters**:
    -request: Borrow request including the name of the member and the title of the book
    -requests: HTTP request containing the member token

    **Returns**:
    -A success message if the book is returned successfully
    -An error message if the book is not borrowed or the member is not found
    """

    returned_books = get_returned_books_data(book_body, db,user)
    if returned_books:
     
            content={
                "message": "Book returned successfully",
                "returned_books": returned_books,
            },
            return JSONResponse(status_code=200, content=content)
    else:
        raise HTTPException(
            status_code=400, detail="Unable to return books,please check it"
        )
