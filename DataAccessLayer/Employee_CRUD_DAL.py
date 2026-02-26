

from Model.EmployeeModel import Employee_Model_Class
import pyodbc

class Employee_CRUD_DAL_Class:
    def __init__(self):
        pass

    def register_employee(self, employee_object: Employee_Model_Class):
        connection_string: str= "Driver={ODBC Driver 17 for SQL Server};Server=your_server_here;Database=SematecLearningManagementSystem;UID=sa;PWD=your_password_here"
        command_text = "Exec [dbo].[InsertEmployee] ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?"
        with pyodbc.connect(connection_string) as connection:

            curses = connection.cursor()
            curses.execute(command_text, employee_object.FirstName, employee_object.LastName,
                                            employee_object.Birthdate, employee_object.Marital_Status, employee_object.NationalCode,
                                            employee_object.Mobile, employee_object.Address, employee_object.Gender, employee_object.EmailAddress,
                                            employee_object.EducationID, employee_object.ManagerID, employee_object.TotalChildren,
                                            employee_object.StartDate, employee_object.InsuranceNumber, employee_object.AccountNumber,
                                            employee_object.HireDate, employee_object.DepartmentID, employee_object.JobID)


            connection.commit()
