# Model/CertificationModel.py

class CertificationModel:
    def __init__(self, certification_title: str, vendor: str, cert_id: int = None):
        self.ID = cert_id
        self.CertificationTitle = certification_title
        self.Vendor = vendor
