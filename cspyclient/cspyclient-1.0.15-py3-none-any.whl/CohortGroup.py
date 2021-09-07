from .Base import Base


class CohortGroup(Base):
    '''
    Cohort group object, to manage all group in cohort
    '''
    ATTRIBUTES = ['_id', 'cohort', 'cohort_id', 'name', 
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = "cohort-groups"

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return super().__repr__(['cohort','name'])

    def add_single_member(self, db_service, member, status='participant'):
        '''
        Add a single cohort member to the current cohort group object
        Parameter:
            db_service: DBService object indicate the server to put on
            member: a cohort member in CohortMember type
            status: the status of cohort member (default participant)
        '''
        if (type(member) is not CohortMember):
            print('ERROR: Data must be instance of Cohort Member')
            return
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort Group undefined')
            return
        if (not getattr(member, '_id', '')):
            print('ERROR: Cohort Member undefined')
            return       
        member.cohort_group_id = self._id
        member.save(db_service)

    def add_members_to_group(self, db_service, members):
        '''
        Add a list of members to the cohort group
        Parameter:
            db_service: DBService object indicate the server to put on
            members: a list of cohort members (each cohort member is in CohortMember type)
        '''
        for member in members:
            self.add_single_member(db_service, member)  

    def get_student_list(self, db_service, output='DataFrame'):
        '''
        Get student information in the current cohort group from database
        Parameter:
            db_service: DBService object indicate the server to put on
            output: kind of multi-value class to holder the result. the default is 'DataFrame'
        Return: result in corresponding output type, each single item is in Student object type
        '''
        if (not getattr(self, '_id', '')):
            print('ERROR: Cohort Group undefined')
            return
        students = db_service.get(f'/cohort-groups/{self._id}/students?page=1&limit=1000')['students']
        return Utils.output_form(Student, students, output)


  
    