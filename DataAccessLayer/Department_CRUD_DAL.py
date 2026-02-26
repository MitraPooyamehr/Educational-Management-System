# DataAccessLayer/Department_CRUD_DAL.py
import pyodbc
from Model.DepartmentModel import DepartmentModel


class Department_CRUD_DAL:
    def __init__(self):
        # ✅ IMPORTANT: Driver 17
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def insert_department(self, dept: DepartmentModel) -> int:
        sql = "EXEC dbo.InsertDepartment ?, ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (dept.DepartmentName, dept.EnglishDepartmentName))
            row = cur.fetchone()
            return int(row[0]) if row else 0

    def update_department(self, dept: DepartmentModel) -> bool:
        sql = "EXEC dbo.UpdateDepartment ?, ?, ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(dept.ID), dept.DepartmentName, dept.EnglishDepartmentName))
            return True

    def delete_department(self, dept_id: int) -> bool:
        sql = "EXEC dbo.DeleteDepartment ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(dept_id),))
            return True

    def get_all_departments(self):
        sql = "EXEC dbo.GetAllDepartments"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()

    def search_departments(self, q: str):
        sql = "EXEC dbo.SearchDepartments ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (q,))
            return cur.fetchall()
