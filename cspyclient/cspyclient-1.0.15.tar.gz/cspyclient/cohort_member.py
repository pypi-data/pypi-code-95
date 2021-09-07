'''
Cohort member class
'''
from .base import Base #pylint: disable=[relative-beyond-top-level]

class CohortMember(Base): #pylint: disable=[too-few-public-methods]
    '''
    Cohort member object, to manage all member of a cohort
    '''
    ATTRIBUTES = ['_id', 'cohort_id', 'member_type', 'member_id', 'status',
                    'withdrawn_at', 'progress_score', 'cohort_group_id',
                    'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['cohort', 'member', 'cohort_group']
    name_of_class = "cohort-members"

    def __repr__(self):
        return super().__repr__(['_id','cohort_id','member_id','member_type'])
