# BusinessLogicLayer/Score_CRUD_BLL.py
from Model.ScoreModel import Score_Model_Class
from DataAccessLayer.Score_CRUD_DAL import Score_CRUD_DAL_Class


class Score_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Score_CRUD_DAL_Class()

    # combo lists
    def get_students_list(self):
        return self.dal.get_students_list()

    def get_teachers_list(self):
        return self.dal.get_teachers_list()

    def get_courses_list(self):
        return self.dal.get_courses_list()

    # CRUD
    def get_all_scores(self):
        return self.dal.get_all_scores()

    def search_scores(self, q: str):
        return self.dal.search_scores(q)

    def insert_score(self, score_obj: Score_Model_Class):
        return self.dal.insert_score(score_obj)

    def update_score(self, score_obj: Score_Model_Class):
        return self.dal.update_score(score_obj)

    def delete_score(self, student_id: int, course_id: int, teacher_id: int, term_number: int):
        return self.dal.delete_score(student_id, course_id, teacher_id, term_number)
