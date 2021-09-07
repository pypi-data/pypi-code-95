'''
Class student
'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class Student(Base):
    '''
    Student object to manage all students
    '''
    ATTRIBUTES = ['_id', 'name', 'email', 'sub_emails', 'first_name', 'last_name', 'gender',
                  'phone_number', 'linked_in_url', 'current_employment_status',
                  'current_company', 'engineering_experience', 'personal_website', 'github_profile',
                  'address', 'city', 'country', 'progress_score', 'status', 'cohort_group_name',
                  'cohort_member_id', 'created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = 'students'

    def __repr__(self):
        return super().__repr__(['name','email'])

    @classmethod
    def add_bulk(cls, std_list):
        '''
        Create multiple new students information and send back to database
        Parameter:
            db_service: DBService object indicate the server to put on
            std_list: data of students arrange in a list (with each student information required
             corresponding to the data in class)
        '''
        return [cls.create(std) for std in std_list]

    @classmethod
    def find_one_by_email(cls, email):
        '''
        Get the first value of the class that match the email
        Parameter:
            db_service: DBService object indicate the server to put on
            email: email in query
        Return: result in current object type
        '''
        return cls.find_one(filter_={'email': email})
