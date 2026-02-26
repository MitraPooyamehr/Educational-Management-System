class Student_Model_Class:
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
        FirstRegisterdate,
        EnglishFirstName,
        EnglishLastName,
        PhotoBytes=None
    ):
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

        self.FirstRegisterdate = FirstRegisterdate
        self.EnglishFirstName = EnglishFirstName
        self.EnglishLastName = EnglishLastName
        self.PhotoBytes = PhotoBytes
