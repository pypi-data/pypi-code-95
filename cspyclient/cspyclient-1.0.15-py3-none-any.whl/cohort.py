'''Cohort class'''
import pandas as pd
from .cohort_member import CohortMember
from .base import Base #pylint: disable=[relative-beyond-top-level]
from .student import Student
from .user import User
from .utils import Utils #pylint: disable=[relative-beyond-top-level]


class Cohort(Base):
    '''
    Cohort object to manage all cohorts
    '''
    ATTRIBUTES = ['_id', 'course', 'course_id', 'name', 'slug', 'contact_list_sheet_url',
                 'support_email', 'prework_url', 'start_date', 'demo_day_date',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['course']
    name_of_class = 'cohorts'

    def __repr__(self):
        return super().__repr__(['_id','name'])

    def enroll_single_student(self, student, status='PARTICIPANT'):
        '''
        Add a new student information to database
        Parameter:
            student: Student object include data of students to be added
            status: status of the current student in cohort (default 'PARTICIPANT')
        '''
        if type(student) is not Student:
            print('ERROR: Data must be instance of Student')
            return
        if not getattr(self, '_id', ''):
            print('ERROR: Cohort undefined')
            return
        if not getattr(student, '_id', ''):
            print('ERROR: Missing student ID')
            return
        data = {'cohortId': self._id, 'memberType':'Student', 'memberId':student._id,
                'status': status}
        CohortMember.create(data)

    def enroll_students(self, students, status='PARTICIPANT'):
        '''
        Add multiple students information to database
        Parameter:
            students: Multiple student object in a iterable type, include data of students to
            be added
            status: status of the current students in cohort (default 'PARTICIPANT')
        '''
        for student in students:
            self.enroll_single_student(student, status)

    def enroll_single_staff(self, staff, status='PARTICIPANT'):
        '''
        Add a new staff information to database
        Parameter:
            staff: User object include data of staffs to be added
            status: status of the current staff in cohort (default 'PARTICIPANT')
        '''
        if type(staff) is not User:
            print('ERROR: Data must be instance of User')
            return
        if not getattr(self, '_id', ''):
            print('ERROR: Cohort undefined')
            return
        if not getattr(staff, '_id', ''):
            print('ERROR: User undefined')
            return
        data = {'cohortId': self._id, 'memberType':'User', 'memberId':staff._id,
                'status': status}
        CohortMember.create(data)

    def enroll_staffs(self, staffs, status='PARTICIPANT'):
        '''
        Add multiple staffs information to database
        Parameter:
            staffs: Multiple User object in a iterable type, include data of staffs to
            be added
            status: status of the current staffs in cohort (default 'PARTICIPANT')
        '''
        for user in staffs:
            self.enroll_single_staff(user, status)

    def get_student_list(self):
        '''
        Get student information in the current cohort from database

        Return: a pandas DataFrame of students including cohort member, cohort group
        '''
        if not getattr(self, '_id', ''):
            print('ERROR: Cohort undefined')
            return
        from_server = self.db_service.get(f'/cohorts/{self._id}/students')
        try:
            rows = pd.DataFrame(from_server['students']) if from_server['students'] else []
            total = from_server['totalNumber']
            return rows, total
        except:
            return [], 0

    def get_staff_list(self):
        '''
        Get staff information in the current cohort from database

        Return: a pandas DataFrame of instructors and TAs who teach the cohort
        '''
        if not getattr(self, '_id', ''):
            print('ERROR: Cohort undefined')
            return
        from_server = self.db_service.get(f'/cohorts/{self._id}/staffs')
        try:
            rows = pd.DataFrame(from_server['staffs']) if from_server['staffs'] else []
            total = from_server['totalNumber']
            return rows, total
        except:
            return [], 0

    @classmethod
    def find_one_by_name(cls, the_name):
        '''
        Get the first value of the class that match a key, with default key is its 'name'
        Parameter:
            the_name: the current key in query
        Return: result in current object type
        '''
        return cls.find_one(filter_={'name': the_name})
