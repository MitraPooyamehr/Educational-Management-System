from Model.StudentModel import Student_Model_Class
from DataAccessLayer.Student_CRUD_DAL import Student_CRUD_DAL_Class

class Student_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Student_CRUD_DAL_Class()

    def insert_student(self, st: Student_Model_Class):
        return self.dal.insert_student(st)

    def update_student(self, person_id: int, st: Student_Model_Class):
        return self.dal.update_student(person_id, st)

    def delete_student(self, person_id: int):
        return self.dal.delete_student(person_id)

    def get_all_students(self):
        return self.dal.get_all_students()

    def search_students(self, q: str):
        return self.dal.search_students(q)

    def get_student_by_id(self, person_id: int):
        return self.dal.get_student_by_id(person_id)
