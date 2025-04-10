from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.extension import get_db
from core.auth.auth_bearer import JWTBearer
from core.auth.auth_handler import get_current_user
from api.entrypoint.admin.models import CreateModel, AdminLogins, NewMember, NewBooks
from core.handlers.request_handlers.response_handlers import json_response
from modules.admin.handlers import (
    add_admin,
    get_admins,
    get_member,
    add_user_books,
    view_available_books,
    view_all_members,
    view_member_by_id,
)
from api.entrypoint.admin.responses import MemberResponse, MembersListResponse
from modules.admin.exception_handler import (
    InvalidAdminCredentialsError,
)
from api.utils.logger import get_logger


logger = get_logger()
router = APIRouter()


@router.post("/")
def create_admin(admin: CreateModel, db: Session = Depends(get_db)):
    logger.info(f"Creating admin: {admin.username}")
    success = add_admin(admin, db)
    if success:
        return json_response(
            status_code=201, content={"id": success.admin_id, "name": success.username}
        )


@router.post("/login")
def login_admin(admin_data: AdminLogins, db: Session = Depends(get_db)):
    try:
        login_result = get_admins(admin_data, db)
        return {
            "message": "Login Success",
            "admin_id": login_result["admin_id"],
            "token": login_result["token"],
        }
    except InvalidAdminCredentialsError:
        return {"error": "Invalid credentials"}


@router.post("/add_member", dependencies=[Depends(JWTBearer())])
def add_member(
    request: Request,
    newuser: NewMember,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    members = get_member(request, newuser, db, user)
    if members:
        return json_response(
            status_code=201,
            content={"message": "Member added successfully", "new_member": members},
        )


@router.post("/add_books", dependencies=[Depends(JWTBearer())])
def add_books(
    request: Request,
    newbook: NewBooks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = add_user_books(request, newbook, db, user)
    if "new_book" in result:
        return json_response(content=result, status_code=201)


@router.get("/view_available_books", dependencies=[Depends(JWTBearer())])
def view_books(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    viewBooks = view_available_books(request, db, user)
    return json_response(content=viewBooks, status_code=200)


@router.get(
    "/view_members",
    response_model=MembersListResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_members(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return view_all_members(request, db, user)


@router.get(
    "/view_members/{member_id}",
    response_model=MemberResponse,
    dependencies=[Depends(JWTBearer())],
)
def view_member_by_id_route(
    member_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return view_member_by_id(member_id, db, user)
