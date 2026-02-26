# Model/EducationModel.py

class Education_Model_Class:
    def __init__(self, education_title: str, english_education: str, education_id: int | None = None):
        self.ID = education_id
        self.EducationTitle = education_title
        self.EnglishEducation = english_education
