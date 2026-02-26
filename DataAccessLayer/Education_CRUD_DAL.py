# DataAccessLayer/Education_CRUD_DAL.py
import pyodbc
from Model.EducationModel import Education_Model_Class


class Education_CRUD_DAL_Class:
    def __init__(self):
        # ✅ IMPORTANT: use ODBC Driver 17 (NOT "SQL Server")
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def insert_education(self, education_obj: Education_Model_Class) -> int | None:
        sql = "EXEC dbo.InsertEducation ?,?"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, (education_obj.EducationTitle, education_obj.EnglishEducation))
                row = cur.fetchone()
                if row:
                    return int(row[0])
                return None
        except Exception as e:
            raise RuntimeError(f"InsertEducation Error: {e}")

    def update_education(self, education_obj: Education_Model_Class) -> bool:
        sql = "EXEC dbo.UpdateEducation ?,?,?"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, (education_obj.ID, education_obj.EducationTitle, education_obj.EnglishEducation))
                return True
        except Exception as e:
            raise RuntimeError(f"UpdateEducation Error: {e}")

    def delete_education(self, education_id: int) -> bool:
        sql = "EXEC dbo.DeleteEducation ?"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, (education_id,))
                return True
        except Exception as e:
            raise RuntimeError(f"DeleteEducation Error: {e}")

    def get_all_educations(self):
        sql = "EXEC dbo.GetAllEducations"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
        except Exception as e:
            raise RuntimeError(f"GetAllEducations Error: {e}")

    def search_educations(self, search_text: str):
        sql = "EXEC dbo.SearchEducations ?"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, (search_text,))
                rows = cur.fetchall()
                return rows
        except Exception as e:
            raise RuntimeError(f"SearchEducations Error: {e}")

    def get_all_education_list(self):
        # برای combobox (اگر خواستی جای دیگه استفاده کنی)
        sql = "EXEC dbo.GetAllEducationList"
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
        except Exception as e:
            raise RuntimeError(f"GetAllEducationList Error: {e}")
