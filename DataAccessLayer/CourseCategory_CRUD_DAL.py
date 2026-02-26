# DataAccessLayer/CourseCategory_CRUD_DAL.py

import pyodbc
from Model.CourseCategoryModel import CourseCategory_Model_Class


class CourseCategory_CRUD_DAL_Class:
    def __init__(self):
        # ✅ IMPORTANT: Driver 17 to avoid HYCOO error
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def insert_course_category(self, obj: CourseCategory_Model_Class) -> int:
        sql = "EXEC dbo.InsertCourseCategory ?,?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (obj.CourseCategoryName, obj.EnglishCourseCategoryName))
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def update_course_category(self, obj: CourseCategory_Model_Class) -> bool:
        sql = "EXEC dbo.UpdateCourseCategory ?,?,?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(obj.ID), obj.CourseCategoryName, obj.EnglishCourseCategoryName))
            return True

    def delete_course_category(self, course_category_id: int) -> bool:
        sql = "EXEC dbo.DeleteCourseCategory ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(course_category_id),))
            return True

    def get_all_course_categories(self):
        sql = "EXEC dbo.GetAllCourseCategories"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            return rows

    def search_course_categories(self, q: str):
        sql = "EXEC dbo.SearchCourseCategories ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (q,))
            rows = cur.fetchall()
            return rows
