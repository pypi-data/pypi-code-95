'''
Submission grade class
'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class SubmissionGrade(Base): #pylint: disable=[too-few-public-methods]
    '''
    Submission grade class, to track all submission grade
    '''
    ATTRIBUTES = ['_id', 'assignment_id', 'cohort_member_id', 'grader_id', 'notes',
                    'total_score', 'status', 'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['assignment', 'grader', 'cohort_member']
    name_of_class = "submission-grades"

    def __repr__(self):
        return super().__repr__(['_id', 'assignment_id', 'cohort_member_id', 'grader_id', 'total_score'])

    def save(self):
        '''
        Update data of the object in server, if the object has not in server yet,
        create a new instance and put the object on
        '''
        if not self.db_service.is_user():
            print('ERROR: Login required')
            return

        if not getattr(self, '_id', ''):
            self.grader_id = self.db_service.get_current_user_id()
            new_data = self.db_service.post(f'/{self.name_of_class}', self.to_json())
            if new_data and '_id' in new_data:
                self.set_attributes(new_data)
        else:
            self.grader_id = self.db_service.get_current_user_id()
            updated_data = self.db_service.put(f'/{self.name_of_class}/{self._id}', self.to_json())
            if updated_data and '_id' in updated_data:
                self.set_attributes(updated_data)