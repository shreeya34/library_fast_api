class Member:
    def __init__(self, member_id, name, role,password):
        self.member_id = member_id
        self.name = name
        self.role = role
        self.password = password
        
    def __str__(self):
        return f"{self.member_id},{self.name},{self.role}"