from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sql import Base

class Admin(Base):
    __tablename__ = 'admin'
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, unique=True, nullable=False) 
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True)
    role = Column(String)
    password = Column(String)

# class Book(Base):
#     __tablename__ = 'book'
#     id = Column(Integer,primary_key=True,index=True)
#     title = Column(String)
#     author = Column(String)
#     stock = Column(Integer)
#     available = Column(Boolean)
    
# class BorrowedBooks(Base):
#     __tablename__ = 'borrowed_books'
#     id = Column(Integer,primary_key=True,index=True)
#     title = Column(String)
#     member_id = Column(Integer)
#     borrow_date = Column(DateTime, default=datetime.now)
#     expiry_date = Column(DateTime)
    
    

    
    
    

