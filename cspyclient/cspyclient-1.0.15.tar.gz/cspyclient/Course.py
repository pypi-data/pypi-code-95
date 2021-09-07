'''Class course'''
from .base import Base #pylint: disable=[relative-beyond-top-level]


class Course(Base):
    '''
    Course object to manage all courses
    '''
    ATTRIBUTES = ['_id', 'name', 'slug', 'duration', 'is_published', 'is_enrollable',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    name_of_class = 'courses'

    def __repr__(self):
        return super().__repr__(['_id','name'])

    @classmethod
    def find_one_by_name(cls, the_name):
        '''
        Get the first value of the class that match a key, with default key is its 'name'
        Parameter:
            the_name: the current key in query
        Return: result in current object type
        '''
        return cls.find_one(filter_={'name': the_name})
