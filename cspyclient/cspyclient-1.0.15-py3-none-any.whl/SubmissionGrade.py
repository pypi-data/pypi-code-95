from .Base import Base


class SubmissionGrade(Base):
    '''
    Submission grade class, to track all submission grade
    '''
    ATTRIBUTES = ['_id', 'submission', 'submission_id', 'grader', 'grader_id', 'notes', 'total_score', 'status',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = "submission-grades"

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return super().__repr__(['name','_id'])