# Model/ScoreModel.py

class Score_Model_Class:
    def __init__(self, student_id: int, course_id: int, teacher_id: int, term_number: int, score: int):
        self.StudentID = student_id
        self.CourseID = course_id
        self.TeacherID = teacher_id
        self.TermNumber = term_number
        self.Score = score
