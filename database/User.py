class User:
    def __init__(self, id, firstname, lastname, email, password, phone=None):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.phone = phone
    def __repr__(self):
        return f'<User: {self.username}>'