# BusinessLogicLayer/Certification_CRUD_BLL.py
from Model.CertificationModel import CertificationModel
from DataAccessLayer.Certification_CRUD_DAL import Certification_CRUD_DAL


class Certification_CRUD_BLL:
    def __init__(self):
        self.dal = Certification_CRUD_DAL()

    def add(self, cert: CertificationModel):
        return self.dal.insert_certification(cert)

    def update(self, cert: CertificationModel):
        return self.dal.update_certification(cert)

    def delete(self, cert_id: int):
        return self.dal.delete_certification(cert_id)

    def get_all(self):
        return self.dal.get_all_certifications()

    def search(self, q: str):
        return self.dal.search_certifications(q)
