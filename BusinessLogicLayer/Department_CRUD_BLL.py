# BusinessLogicLayer/Department_CRUD_BLL.py
from Model.DepartmentModel import DepartmentModel
from DataAccessLayer.Department_CRUD_DAL import Department_CRUD_DAL


class Department_CRUD_BLL:
    def __init__(self):
        self.dal = Department_CRUD_DAL()

    def add_department(self, dept: DepartmentModel) -> int:
        return self.dal.insert_department(dept)

    def edit_department(self, dept: DepartmentModel) -> bool:
        return self.dal.update_department(dept)

    def remove_department(self, dept_id: int) -> bool:
        return self.dal.delete_department(dept_id)

    def get_all(self):
        return self.dal.get_all_departments()

    def search(self, q: str):
        return self.dal.search_departments(q)
