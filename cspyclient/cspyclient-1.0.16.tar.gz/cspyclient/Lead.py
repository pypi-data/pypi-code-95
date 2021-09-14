'''Class lead'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class Lead(Base):
    '''
    Lead object to manage all leads
    '''
    ATTRIBUTES = ['_id', 'cohort_id', 'assignment_id', 'cohort_name',
                'assignment_name', 'email', 'name', 'created_by', 'updated_by', 'created_at',
                'updated_at']
    REFS = ['cohort', 'assignment']
    name_of_class = "leads"

    def __repr__(self):
        return super().__repr__(['_id','name'])

    @classmethod
    def find_one_by_email(cls, email):
        '''
        Get the first value of the class that match the email
        Parameter:
            db_service: DBService object indicate the server to put on
            email: email in query
        Return: result in current object type
        '''
        return cls.find_one_by_name(cls.db_service, email, optional_param='email')
