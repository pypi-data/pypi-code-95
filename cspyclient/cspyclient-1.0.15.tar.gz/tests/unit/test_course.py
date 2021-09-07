import copy
from cspyclient import Course
from .mock_data import mock_course

def test_create_with_same_name():
	'''Should not allow to create a new course with the same name'''
	data = copy.copy(mock_course)
	del data['_id']
	same_course = Course.create(data)
	assert getattr(same_course, '_id', None) is None

def test_get_courses():
	'''Should get the list of courses with panigation'''
	courses, total_number  = Course.find(output='object', filter_={'name': mock_course['name']})
	assert total_number == 1
	assert mock_course['_id'] == courses[0]._id

def test_get_course_by_id():
	'''Should get a single course'''
	course = Course.find_by_id(mock_course['_id'])
	assert course._id == mock_course['_id']