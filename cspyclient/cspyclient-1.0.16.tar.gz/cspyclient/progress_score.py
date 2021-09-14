'''Class progress score'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class ProgressScore(Base): #pylint: disable=[too-few-public-methods]
    '''
    Progress score object, to track all of socring progress
    '''
    ATTRIBUTES = ['_id', 'cohort_member_id', 'activity',
                  'notes', 'score','created_by', 'updated_by', 'created_at',
                  'updated_at']
    REFS = ['cohort_member']
    name_of_class = "progress-scores"

    def __repr__(self):
        return super().__repr__(['_id','cohort_member_id','activity','score'])
