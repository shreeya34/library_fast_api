from datetime import datetime
from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
)
from database.sql import Base
from sqlalchemy.orm import relationship



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
