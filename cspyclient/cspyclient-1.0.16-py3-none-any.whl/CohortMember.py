from .Base import Base

class CohortMember(Base):
    '''
    Cohort member object, to manage all member of a cohort
    '''
    ATTRIBUTES = ['_id', 'cohort', 'cohort_id', 'member_type', 'member', 'member_id', 'status', 'withdrawn_at', 'progress_score',
                        'cohort_group', 'cohort_group_id',
                        'created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = "cohort-members"

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return super().__repr__(['cohort','member','member_type'])