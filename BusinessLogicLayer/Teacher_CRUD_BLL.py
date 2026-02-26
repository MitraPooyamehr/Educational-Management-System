from Model.TeacherModel import Teacher_Model_Class
from DataAccessLayer.Teacher_CRUD_DAL import Teacher_CRUD_DAL_Class


class Teacher_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Teacher_CRUD_DAL_Class()

    def register_teacher(self, teacher: Teacher_Model_Class):
        return self.dal.register_teacher(teacher)

    def update_teacher(self, teacher: Teacher_Model_Class):
        return self.dal.update_teacher(teacher)

    def delete_teacher(self, person_id: int):
        return self.dal.delete_teacher(person_id)

    def get_all_teachers(self):
        return self.dal.get_all_teachers()

    def search_teachers(self, q: str):
        return self.dal.search_teachers(q)