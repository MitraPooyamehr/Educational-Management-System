# BusinessLogicLayer/CourseCategory_CRUD_BLL.py

from Model.CourseCategoryModel import CourseCategory_Model_Class
from DataAccessLayer.CourseCategory_CRUD_DAL import CourseCategory_CRUD_DAL_Class


class CourseCategory_CRUD_BLL_Class:
    def __init__(self):
        self.dal = CourseCategory_CRUD_DAL_Class()

    def register_course_category(self, obj: CourseCategory_Model_Class) -> int:
        return self.dal.insert_course_category(obj)

    def update_course_category(self, obj: CourseCategory_Model_Class) -> bool:
        return self.dal.update_course_category(obj)

    def delete_course_category(self, course_category_id: int) -> bool:
        return self.dal.delete_course_category(course_category_id)

    def get_all_course_categories(self):
        return self.dal.get_all_course_categories()

    def search_course_categories(self, q: str):
        return self.dal.search_course_categories(q)
