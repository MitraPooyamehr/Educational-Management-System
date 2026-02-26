# DataAccessLayer/Course_CRUD_DAL.py

import pyodbc
from Model.CourseModel import Course_Model_Class


class Course_CRUD_DAL_Class:
    def __init__(self):
        # ✅ IMPORTANT: ODBC Driver 17
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

    # ---------------- helpers ----------------
    def _fetch_rows(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            cols = [d[0] for d in cur.description] if cur.description else []
            return rows, cols

    def _exec_only(self, sql: str, params=()):
        with pyodbc.connect(self.connection_string) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return True

    # ---------------- combobox sources ----------------
    def get_all_course_categories(self):
        rows, cols = self._fetch_rows("EXEC dbo.GetAllCourseCategoryList")
        out = []

        if cols:
            # try to detect name columns
            norm = [c.lower() for c in cols]
            id_idx = norm.index("id") if "id" in norm else 0

            # priority: EnglishCourseCategoryName then CourseCategoryName
            name_idx = None
            for k in ["englishcoursecategoryname", "coursecategoryname"]:
                if k in norm:
                    name_idx = norm.index(k)
                    break
            if name_idx is None:
                name_idx = 1 if len(cols) > 1 else 0

            for r in rows:
                out.append((int(r[id_idx]), str(r[name_idx]).strip()))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))

        out = [x for x in out if x[1]]
        out.sort(key=lambda x: x[0])
        return out

    def get_prerequisite_courses(self):
        rows, cols = self._fetch_rows("EXEC dbo.GetPrerequisiteCourseList")
        out = []

        if cols:
            norm = [c.lower() for c in cols]
            id_idx = norm.index("id") if "id" in norm else 0
            name_idx = None
            for k in ["coursename", "englishcoursename"]:
                if k in norm:
                    name_idx = norm.index(k)
                    break
            if name_idx is None:
                name_idx = 1 if len(cols) > 1 else 0

            for r in rows:
                out.append((int(r[id_idx]), str(r[name_idx]).strip()))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))

        out = [x for x in out if x[1]]
        out.sort(key=lambda x: x[0])
        return out

    # ---------------- CRUD ----------------
    def get_all_courses(self):
        return self._fetch_rows("EXEC dbo.GetAllCourses")

    def search_courses(self, search_text: str):
        return self._fetch_rows("EXEC dbo.SearchCourses ?", (search_text,))

    def insert_course(self, course: Course_Model_Class) -> int:
        sql = "EXEC dbo.InsertCourse ?,?,?,?,?,?,?,?,?,?,?,?"
        params = (
            int(course.CourseCode),
            course.CourseName,
            course.EnglishCourseName,
            course.Description,
            int(course.Duration),
            course.Syllabus,
            int(course.Cost),
            course.SyllabusFile,  # bytes (required)
            course.Status,
            course.CourseCategoryID,
            course.PrerequisitCourseID
        )

        rows, _ = self._fetch_rows(sql, params)
        if rows and len(rows[0]) > 0:
            return int(rows[0][0])
        return 0

    def update_course(self, course: Course_Model_Class) -> bool:
        sql = "EXEC dbo.UpdateCourse ?,?,?,?,?,?,?,?,?,?,?,?"
        params = (
            int(course.CourseID),
            int(course.CourseCode),
            course.CourseName,
            course.EnglishCourseName,
            course.Description,
            int(course.Duration),
            course.Syllabus,
            int(course.Cost),
            course.SyllabusFile,  # None => keep old in SP (COALESCE)
            course.Status,
            course.CourseCategoryID,
            course.PrerequisitCourseID
        )
        return self._exec_only(sql, params)

    def delete_course(self, course_id: int) -> bool:
        return self._exec_only("EXEC dbo.DeleteCourse ?", (int(course_id),))
