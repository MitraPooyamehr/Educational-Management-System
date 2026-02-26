# DataAccessLayer/Job_CRUD_DAL.py
import pyodbc
from Model.JobModel import Job_Model_Class


class Job_CRUD_DAL_Class:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    # ---------- helpers ----------
    def _connect(self):
        return pyodbc.connect(self.connection_string, autocommit=True)

    # ---------- CRUD ----------
    def insert_job(self, job_obj: Job_Model_Class) -> int | None:
        sql = "EXEC dbo.InsertJob ?"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, (job_obj.JobTitle,))
                row = cur.fetchone()
                return int(row[0]) if row else None
        except Exception as e:
            raise RuntimeError(f"InsertJob failed: {e}")

    def update_job(self, job_obj: Job_Model_Class) -> bool:
        sql = "EXEC dbo.UpdateJob ?, ?"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, (int(job_obj.ID), job_obj.JobTitle))
                row = cur.fetchone()
                # SP returns AffectedRows
                return bool(row and int(row[0]) > 0)
        except Exception as e:
            raise RuntimeError(f"UpdateJob failed: {e}")

    def delete_job(self, job_id: int) -> bool:
        sql = "EXEC dbo.DeleteJob ?"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, (int(job_id),))
                row = cur.fetchone()
                return bool(row and int(row[0]) > 0)
        except Exception as e:
            raise RuntimeError(f"DeleteJob failed: {e}")

    def get_all_jobs(self) -> list[Job_Model_Class]:
        sql = "EXEC dbo.GetAllJobs"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                out = []
                for r in rows:
                    out.append(Job_Model_Class(job_title=str(r[1]), job_id=int(r[0])))
                return out
        except Exception as e:
            raise RuntimeError(f"GetAllJobs failed: {e}")

    def search_jobs(self, text: str) -> list[Job_Model_Class]:
        sql = "EXEC dbo.SearchJobs ?"
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(sql, (text,))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    out.append(Job_Model_Class(job_title=str(r[1]), job_id=int(r[0])))
                return out
        except Exception as e:
            raise RuntimeError(f"SearchJobs failed: {e}")
