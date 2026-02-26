from Model.EmployeeModel import Employee_Model_Class
from DataAccessLayer.Employee_CRUD_DAL import Employee_CRUD_DAL_Class


class Employee_CRUD_BLL_Class:
    def __init__(self):
        pass

    def register_employee(self, employee_object: Employee_Model_Class):
        employee_crud_dal_object = Employee_CRUD_DAL_Class()
        employee_crud_dal_object.register_employee()
