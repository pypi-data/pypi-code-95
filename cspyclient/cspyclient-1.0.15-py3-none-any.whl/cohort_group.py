'''
Cohort group class
'''
import pandas as pd
from .cohort_member import CohortMember
from .base import Base


class CohortGroup(Base):
    '''
    Cohort group object, to manage all group in cohort
    '''
    ATTRIBUTES = ['_id', 'cohort_id', 'name',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['cohort']
    name_of_class = "cohort-groups"

    def __repr__(self):
        return super().__repr__(['_id','name'])

    def add_single_member(self, member, status='participant'):
        '''
        Add a single cohort member to the current cohort group object
        Parameter:
            db_service: DBService object indicate the server to put on
            member: a cohort member in CohortMember type
            status: the status of cohort member (default participant)
        '''
        if type(member) is not CohortMember:
            print('ERROR: Data must be instance of Cohort Member')
            return
        if not getattr(self, '_id', ''):
            print('ERROR: Missing cohort group ID')
            return
        if not getattr(member, '_id', ''):
            print('ERROR: Missing Cohort Member ID')
            return
        member.cohort_group_id = self._id
        member.save()

    def add_members(self, members):
        '''
        Add a list of members to the cohort group
        Parameter:
            members: a list of cohort members (each cohort member is in CohortMember type)
        '''
        for member in members:
            self.add_single_member(member)

    def get_member_list(self):
        '''
        Get member information in the current cohort group from database

        Return: a pandas DataFrame of members who are in the cohort group
        '''
        if not getattr(self, '_id', ''):
            print('ERROR: Cohort Group undefined')
            return
        from_server = self.db_service.get(f'/cohort-groups/{self._id}/members')
        try:
            rows = pd.DataFrame(from_server['members']) if from_server['members'] else []
            total = from_server['totalNumber']
            return rows, total
        except:
            return [], 0
