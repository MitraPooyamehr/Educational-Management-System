# DataAccessLayer/Certification_CRUD_DAL.py
import pyodbc
from Model.CertificationModel import CertificationModel


class Certification_CRUD_DAL:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    def _query(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            return rows

    def _exec(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return True

    # ---------- CRUD ----------
    def insert_certification(self, cert: CertificationModel):
        rows = self._query("EXEC dbo.InsertCertification ?, ?", (cert.CertificationTitle, cert.Vendor))
        if rows and len(rows) > 0:
            return int(rows[0][0])
        return None

    def update_certification(self, cert: CertificationModel):
        return self._exec("EXEC dbo.UpdateCertification ?, ?, ?",
                          (int(cert.ID), cert.CertificationTitle, cert.Vendor))

    def delete_certification(self, cert_id: int):
        return self._exec("EXEC dbo.DeleteCertification ?", (int(cert_id),))

    def get_all_certifications(self):
        return self._query("EXEC dbo.GetAllCertifications")

    def search_certifications(self, q: str):
        return self._query("EXEC dbo.SearchCertifications ?", (q,))
