from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, Integer, String, Boolean, DateTime
from sql import Base
import uuid
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = 'admin'
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, unique=True, nullable=False) 
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    
class AdminLogin(Base):
    __tablename__ = 'admin_logins'
    
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    member_id = Column(String, nullable=True) 
    status = Column(String, nullable=False)
    password = Column(String, nullable=False)
    login_time = Column(TIMESTAMP, nullable=True)

class Book(Base):
    __tablename__ = 'book' 
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    author = Column(String)
    stock = Column(Integer)
    available = Column(Boolean)
    
    availability = relationship("BookAvailability", back_populates="book", uselist=False)
    
class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
  

    
class BookAvailability(Base):
    __tablename__ = "book_availability"


    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book.id"), unique=True, nullable=False) 
    title = Column(String, index=True) 
    available = Column(Boolean, default=True)
    book = relationship("Book", back_populates="availability")
    
class ViewMembers(Base):
    __tablename__ = 'view_members'
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    
class MemberLogins(Base):
    __tablename__='member_logins'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name=Column(String,nullable=False)
    member_id = Column(String, nullable=False)  
    status=Column(String,nullable=False)
    password = Column(String,nullable=False)
    login_time = Column(TIMESTAMP, nullable=True)
       
    
    
# class BorrowedBooks(Base):
#     __tablename__ = 'borrowed_books'
#     id = Column(Integer,primary_key=True,index=True)
#     title = Column(String)
#     member_id = Column(Integer)
#     borrow_date = Column(DateTime, default=datetime.now)
#     expiry_date = Column(DateTime)
    
    

    
    
    

