# BusinessLogicLayer/Education_CRUD_BLL.py
from Model.EducationModel import Education_Model_Class
from DataAccessLayer.Education_CRUD_DAL import Education_CRUD_DAL_Class


class Education_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Education_CRUD_DAL_Class()

    def register_education(self, education_obj: Education_Model_Class) -> int | None:
        return self.dal.insert_education(education_obj)

    def update_education(self, education_obj: Education_Model_Class) -> bool:
        return self.dal.update_education(education_obj)

    def delete_education(self, education_id: int) -> bool:
        return self.dal.delete_education(education_id)

    def get_all_educations(self):
        return self.dal.get_all_educations()

    def search_educations(self, search_text: str):
        return self.dal.search_educations(search_text)
