Library Management System Using FastApi

# Overview
This is a FastAPI-based Library Management System that allows administrators to manage books and members.Where admin can add books, add member, view member, view avilable books and members to borrow and return books.


# Installation

1. Create a virtual environment 

```bash
python -m venv env

```
2. Install dependencies:

```bash
pip install -r requirement.txt

```

# Running the Application

```bash

fastapi dev main.py

```
The API will be available at: http://127.0.0.1:8000

# Features
1 Admin can:
    1. Create an account
    2. Login
    3. Add member
    4. Add books
    5. View avilable books
    6. View members

2 Member can:
    1. Login
    2. Borrow books
    3. Return books

# Endpoints

1. Admin Endpoints

   1. Create Admin: POST /admin/

   2. Admin Login: POST /login

   3. Add Member: POST /add_member

   4. Add Books: POST /add_books

   5.  View Available Books: GET /view_avilable_books

   6. View Members: GET /view_members

2. Member Endpoints 

    1. Member Login: POST/member/login

    2. Borrow Book: POST/member/borrow_books

    3. Return Book: POST/member/return_book

# Data Storage

The system uses JSON files to store data:
1. admin.json - Stores admin details
2. member.json - Stores member details
3. books.json - Stores book details
4. borrow_logs.json - Store book borrowing records
5. return_logs.json- Store book return records 

# Authentication
1. Admin and member authenticate via token-based authentication
2. Admin actions require an admin token
3. Member actions require a member token

# Dependencies
1. FastAPI
2. Argon2 for password hasing 
3. JSON for data storage


