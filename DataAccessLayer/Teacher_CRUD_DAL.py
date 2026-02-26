import pyodbc
from Model.TeacherModel import Teacher_Model_Class


class Teacher_CRUD_DAL_Class:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def register_teacher(self, teacher: Teacher_Model_Class):

        sql = "EXEC dbo.InsertTeacher ?,?,?,?,?,?,?,?,?,?,?,?,?,?"

        photo_bytes = pyodbc.Binary(teacher.PhotoBytes) if getattr(teacher, 'PhotoBytes', None) else None

        params = (
            teacher.FirstName,
            teacher.LastName,
            teacher.Birthdate,
            teacher.MaritalStatus,
            teacher.NationalCode,
            teacher.Mobile,
            teacher.Address,
            teacher.Gender,
            teacher.EmailAddress,
            teacher.EducationID,
            teacher.InsuranceNumber,
            teacher.AccountNumber,
            teacher.Startdate,
            photo_bytes  # پارامتر جدید
        )
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            return rows

    def update_teacher(self, teacher: Teacher_Model_Class):
        # تغییر مهم 3: اضافه شدن علامت سوال پانزدهم برای Photo در حالت آپدیت
        sql = "EXEC dbo.UpdateTeacher ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?"

        photo_bytes = pyodbc.Binary(teacher.PhotoBytes) if getattr(teacher, 'PhotoBytes', None) else None

        params = (
            teacher.PersonID,
            teacher.FirstName,
            teacher.LastName,
            teacher.Birthdate,
            teacher.MaritalStatus,
            teacher.NationalCode,
            teacher.Mobile,
            teacher.Address,
            teacher.Gender,
            teacher.EmailAddress,
            teacher.EducationID,
            teacher.InsuranceNumber,
            teacher.AccountNumber,
            teacher.Startdate,
            photo_bytes
        )
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return True

    def delete_teacher(self, person_id: int):
        sql = "EXEC dbo.DeleteTeacher ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (person_id,))
            return True

    def get_all_teachers(self):
        sql = "EXEC dbo.GetAllTeachers"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall() if cur.description else []
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols

    def search_teachers(self, q: str):
        sql = "EXEC dbo.SearchTeachers ?"
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, (q,))
            rows = cur.fetchall() if cur.description else []
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols