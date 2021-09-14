from .Base import Base


class ProgressScore(Base):
    '''
    Progress score object, to track all of socring progress
    '''
    ATTRIBUTES = ['_id', 'cohort_member', 'cohort_member_id', 'activity', 'notes', 
                  'score','created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = "progress-scores"

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return super().__repr__(['cohort_member','activity','score'])         
