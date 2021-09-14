'''
Session class
'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class Session(Base): #pylint: disable=[too-few-public-methods]
    '''
    Session object, to track all sessions
    '''
    ATTRIBUTES = ['_id', 'cohort_id', 'session_type', 'location', 'meeting_id', 'start_time', 'end_time',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['cohort']
    name_of_class = "sessions"

    def __repr__(self):
        return super().__repr__(['_id', 'cohort_id','session_type'])
