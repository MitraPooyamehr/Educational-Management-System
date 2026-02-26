class Teacher_Model_Class:
    def __init__(
        self,
        FirstName,
        LastName,
        Birthdate,
        MaritalStatus,
        NationalCode,
        Mobile,
        Address,
        Gender,
        EmailAddress,
        EducationID,
        Startdate,
        InsuranceNumber,
        AccountNumber,
        PersonID=None
    ):
        self.PersonID = PersonID
        self.FirstName = FirstName
        self.LastName = LastName
        self.Birthdate = Birthdate
        self.MaritalStatus = MaritalStatus
        self.NationalCode = NationalCode
        self.Mobile = Mobile
        self.Address = Address
        self.Gender = Gender
        self.EmailAddress = EmailAddress
        self.EducationID = EducationID
        self.Startdate = Startdate
        self.InsuranceNumber = InsuranceNumber
        self.AccountNumber = AccountNumber
