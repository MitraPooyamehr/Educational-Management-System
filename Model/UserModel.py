class User_Model_class:
    def __init__(self, username, password, firstname, lastname, is_admin, expired_date):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname

        self.isAdmin = bool(is_admin)

        self.expired_date = expired_date


    def get_full_name(self):
        return f"{self.firstname} {self.lastname}".strip()