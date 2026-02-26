# Model/DepartmentModel.py

class DepartmentModel:
    def __init__(self, DepartmentName: str, EnglishDepartmentName: str, ID: int = None):
        self.ID = ID
        self.DepartmentName = DepartmentName
        self.EnglishDepartmentName = EnglishDepartmentName
