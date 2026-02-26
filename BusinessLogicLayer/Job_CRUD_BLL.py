# BusinessLogicLayer/Job_CRUD_BLL.py
from Model.JobModel import Job_Model_Class
from DataAccessLayer.Job_CRUD_DAL import Job_CRUD_DAL_Class


class Job_CRUD_BLL_Class:
    def __init__(self):
        self.dal = Job_CRUD_DAL_Class()

    def register_job(self, job_obj: Job_Model_Class) -> int | None:
        return self.dal.insert_job(job_obj)

    def update_job(self, job_obj: Job_Model_Class) -> bool:
        return self.dal.update_job(job_obj)

    def delete_job(self, job_id: int) -> bool:
        return self.dal.delete_job(job_id)

    def get_all_jobs(self) -> list[Job_Model_Class]:
        return self.dal.get_all_jobs()

    def search_jobs(self, text: str) -> list[Job_Model_Class]:
        return self.dal.search_jobs(text)
