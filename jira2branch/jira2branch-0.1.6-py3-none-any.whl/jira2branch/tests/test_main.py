from unittest import TestCase
from jira2branch.__main__ import Utils

class Test(TestCase):
    def test_issue_title_to_branch_name(self):

        branch_name = Utils.issue_title_to_branch_name('WT3-228', 'title', 'fix')
        self.assertEqual('fix/WT3-228_title', branch_name)

        branch_name = Utils.issue_title_to_branch_name('WT3-228', '[FE] Add field', 'fix')
        self.assertEqual('fix/WT3-228_fe-add-field', branch_name)

        branch_name = Utils.issue_title_to_branch_name('WT3-228', 'An admin/manager can view v(v1)', 'fix')
        self.assertEqual('fix/WT3-228_an-admin-manager-can-view-v-v1', branch_name)

        branch_name = Utils.issue_title_to_branch_name('WT3-228', 'Eça de Queirós tinha um cão de caça', 'fix')
        self.assertEqual('fix/WT3-228_eca-de-queiros-tinha-um-cao-de-caca', branch_name)
