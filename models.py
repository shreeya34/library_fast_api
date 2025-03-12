class Book:
    def __init__(self, book_id, title, author_name, stock):
        self.book_id = book_id
        self.title = title
        self.author_name = author_name
        self.stock = stock
        self.available = True
        
    def __str__(self):
        return f"{self.book_id}. {self.title} by {self.author_name}"

class Member:
    def __init__(self, member_id, name, role):
        self.member_id = member_id
        self.name = name
        self.role = role
        
    def __str__(self):
        return f"{self.member_id},{self.name},{self.role}"
    

