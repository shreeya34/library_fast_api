from datetime import datetime
from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
)
from database.sql import Base
import uuid
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)


class AdminLogin(Base):
    __tablename__ = "admin_logins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, nullable=False)
    member_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    password = Column(String, nullable=False)
    login_time = Column(TIMESTAMP, nullable=True)


class Book(Base):
    __tablename__ = "book"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    author = Column(String)
    stock = Column(Integer)
    available = Column(Boolean)

    availability = relationship(
        "BookAvailability", back_populates="book", uselist=False
    )

    borrowed_books = relationship("BorrowedBooks", back_populates="book")
    returned_books = relationship("ReturnBook", back_populates="book")


class Member(Base):
    __tablename__ = "member"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)

    borrowed_books = relationship("BorrowedBooks", back_populates="member")
    returned_books = relationship("ReturnBook", back_populates="member")


class BookAvailability(Base):
    __tablename__ = "book_availability"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(
        UUID(as_uuid=True), ForeignKey("book.id"), unique=True, nullable=False
    )
    title = Column(String, index=True)
    available = Column(Boolean, default=True)
    book = relationship("Book", back_populates="availability")


class ViewMembers(Base):
    __tablename__ = "view_members"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)


class MemberLogins(Base):
    __tablename__ = "member_logins"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    member_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    login_time = Column(TIMESTAMP, nullable=True)


class BorrowedBooks(Base):
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    member_id = Column(String, ForeignKey("member.member_id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book.id"), nullable=False)
    name = Column(String, nullable=False)

    borrow_date = Column(DateTime, default=datetime.now)
    expiry_date = Column(DateTime)

    member = relationship("Member", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")


class ReturnBook(Base):
    __tablename__ = "return_book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    member_id = Column(String, ForeignKey("member.member_id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book.id"), nullable=False)
    name = Column(String, nullable=False)

    return_date = Column(DateTime, default=datetime.now)

    member = relationship("Member", back_populates="returned_books")
    book = relationship("Book", back_populates="returned_books")
