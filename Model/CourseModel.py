# Model/CourseModel.py

class Course_Model_Class:
    def __init__(
        self,
        course_code: int,
        course_name: str,
        english_course_name: str,
        description: str,
        duration: int,
        syllabus: str,
        cost: int,
        status: str,
        course_category_id: int = None,
        prerequisit_course_id: int = None,
        syllabus_file_bytes: bytes = None,
        course_id: int = None
    ):
        self.CourseID = course_id

        self.CourseCode = course_code
        self.CourseName = course_name
        self.EnglishCourseName = english_course_name
        self.Description = description
        self.Duration = duration
        self.Syllabus = syllabus
        self.Cost = cost
        self.Status = status

        self.CourseCategoryID = course_category_id
        self.PrerequisitCourseID = prerequisit_course_id

        self.SyllabusFile = syllabus_file_bytes
