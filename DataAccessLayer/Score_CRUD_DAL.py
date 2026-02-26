# DataAccessLayer/Score_CRUD_DAL.py
import pyodbc
from Model.ScoreModel import Score_Model_Class


class Score_CRUD_DAL_Class:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    # ---------- helpers ----------
    def _fetchall(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols

    def _execute(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return True

    # ---------- Combo lists ----------
    def get_students_list(self):
        rows, cols = self._fetchall("EXEC dbo.GetAllStudentsForScore")
        return rows, cols

    def get_teachers_list(self):
        rows, cols = self._fetchall("EXEC dbo.GetAllTeachersForScore")
        return rows, cols

    def get_courses_list(self):
        rows, cols = self._fetchall("EXEC dbo.GetAllCoursesForScore")
        return rows, cols

    # ---------- CRUD ----------
    def get_all_scores(self):
        rows, cols = self._fetchall("EXEC dbo.GetAllScores")
        return rows, cols

    def search_scores(self, q: str):
        rows, cols = self._fetchall("EXEC dbo.SearchScores ?", (q,))
        return rows, cols

    def insert_score(self, score_obj: Score_Model_Class):
        sql = "EXEC dbo.InsertScore ?,?,?,?,?"
        rows, cols = self._fetchall(sql, (
            score_obj.StudentID,
            score_obj.CourseID,
            score_obj.TeacherID,
            score_obj.TermNumber,
            score_obj.Score
        ))
        return rows, cols

    def update_score(self, score_obj: Score_Model_Class):
        sql = "EXEC dbo.UpdateScore ?,?,?,?,?"
        return self._execute(sql, (
            score_obj.StudentID,
            score_obj.CourseID,
            score_obj.TeacherID,
            score_obj.TermNumber,
            score_obj.Score
        ))

    def delete_score(self, student_id: int, course_id: int, teacher_id: int, term_number: int):
        sql = "EXEC dbo.DeleteScore ?,?,?,?"
        return self._execute(sql, (student_id, course_id, teacher_id, term_number))
