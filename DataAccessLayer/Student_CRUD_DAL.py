import pyodbc
from Model.StudentModel import Student_Model_Class

class Student_CRUD_DAL_Class:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def insert_student(self, st: Student_Model_Class):
        sql = "EXEC dbo.InsertStudent ?,?,?,?,?,?,?,?,?,?,?,?,?,?"
        photo = pyodbc.Binary(st.PhotoBytes) if st.PhotoBytes else None

        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute(
                sql,
                st.FirstName, st.LastName, st.Birthdate, st.MaritalStatus, st.NationalCode,
                st.Mobile, st.Address, st.Gender, st.EmailAddress, st.EducationID,
                st.FirstRegisterdate, st.EnglishFirstName, st.EnglishLastName, photo
            )
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None

    def update_student(self, person_id: int, st: Student_Model_Class):
        sql = "EXEC dbo.UpdateStudent ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?"
        photo = pyodbc.Binary(st.PhotoBytes) if st.PhotoBytes else None

        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute(
                sql,
                person_id,
                st.FirstName, st.LastName, st.Birthdate, st.MaritalStatus, st.NationalCode,
                st.Mobile, st.Address, st.Gender, st.EmailAddress, st.EducationID,
                st.FirstRegisterdate, st.EnglishFirstName, st.EnglishLastName, photo
            )
            conn.commit()
            return True

    def delete_student(self, person_id: int):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.DeleteStudent ?", (person_id,))
            conn.commit()
            return True

    def get_all_students(self):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.GetAllStudents")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols

    def search_students(self, q: str):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.SearchStudents ?", (q,))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols

    def get_student_by_id(self, person_id: int):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.GetStudentById ?", (person_id,))
            row = cur.fetchone()
            cols = [d[0] for d in cur.description] if cur.description else []
            return row, cols

   
    def get_all_education_list(self):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute("EXEC dbo.GetAllEducationList")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols