# BusinessLogicLayer/Course_CRUD_BLL.py

from Model.CourseModel import Course_Model_Class
from DataAccessLayer.Course_CRUD_DAL import Course_CRUD_DAL_Class


class Course_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Course_CRUD_DAL_Class()

    def get_categories(self):
        return self.dal.get_all_course_categories()

    def get_prerequisites(self):
        return self.dal.get_prerequisite_courses()

    def get_all(self):
        return self.dal.get_all_courses()

    def search(self, text: str):
        return self.dal.search_courses(text)

    def insert(self, course: Course_Model_Class) -> int:
        return self.dal.insert_course(course)

    def update(self, course: Course_Model_Class) -> bool:
        return self.dal.update_course(course)

    def delete(self, course_id: int) -> bool:
        return self.dal.delete_course(course_id)
