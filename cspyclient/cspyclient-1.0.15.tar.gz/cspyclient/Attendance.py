'''
Class Attendance
'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class Attendance(Base): #pylint: disable=[too-few-public-methods]
    '''
    Attendance object, to track attendance
    '''
    ATTRIBUTES = ['_id', 'cohort_member_id', 'session_id',
                  'status', 'notes', 'created_by', 'updated_by',
                  'created_at', 'updated_at']
    REFS = ['cohort_member', 'session']
    name_of_class = "attendances"

    def __repr__(self):
        return super().__repr__(['_id', 'cohort_member_id', 'session_id', 'status'])
