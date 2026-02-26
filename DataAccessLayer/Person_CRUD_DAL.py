import pyodbc

class Person_DAL_Class:
    def __init__(self):
        pass

    def get_education_list(self):
        connection_string: str= "Driver={SQL Server};Server=your_server_here;Database=SematecLearningManagementSystem;UID=sa;PWD=your_password_here"
        command_text = "Exec [dbo].[GetAllEducationList]"
        with pyodbc.connect(connection_string) as connection:
            cursor = connection.cursor()
            cursor.execute(command_text,)
            rows = cursor.fetchall()
            return rows
