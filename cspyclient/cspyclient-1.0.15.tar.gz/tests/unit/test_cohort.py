import copy
from cspyclient import Cohort
from .mock_data import mock_cohort

def test_create_with_same_name():
    '''Should not allow to create a new cohort with the same name'''
    data = copy.copy(mock_cohort)
    del data['_id']
    same_cohort = Cohort.create(data)
    assert getattr(same_cohort, '_id', None) is None

def test_get_cohorts():
	'''Should get the list of cohorts with panigation'''
	cohorts, total_number  = Cohort.find(output='object', filter_={'name': mock_cohort['name']})
	assert total_number == 1
	assert mock_cohort['_id'] == cohorts[0]._id