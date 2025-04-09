from sqlalchemy.orm import Session
from db_schema.admin import Admin, Member, ViewMembers


def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()


def get_member_by_name(db: Session, name: str):
    return db.query(Member).filter(Member.name == name).first()


def get_all_members(db: Session):
    return db.query(Member).all()


def get_view_member_by_id(db: Session, member_id: str):
    return db.query(ViewMembers).filter(ViewMembers.member_id == member_id).first()


def get_all_view_members(db: Session):
    return db.query(ViewMembers).all()
