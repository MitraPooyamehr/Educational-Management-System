# Model/JobModel.py

class Job_Model_Class:
    def __init__(self, job_title: str, job_id: int | None = None):
        self.ID = job_id
        self.JobTitle = job_title
