'''
Base class, to implemend all function
'''

from .config import APP_URL
from .utils import Utils #pylint: disable=[relative-beyond-top-level]
from .db_service import DBService #pylint: disable=[relative-beyond-top-level]

class Base:
    '''
    Base class to implemend every other related field
    Attributes:
      ATTRIBUTES: list of key/attribute that a given object have
      name_of_class: name of specific object that implemending this class Base; for inheritance,
      it should be the same name as sub-link to database
      nameOfClassCamel: if class name has space between, manual provide camel case here
    '''
    ATTRIBUTES = []
    REFS = []
    name_of_class = ''
    db_service = DBService(APP_URL)

    def __init__(self, data):
        '''
        Parameter
          data: a dictionary or equivilant data type with key,value organisation of that can be
           used to create the object
        '''
        self.set_attributes(data)

    def set_attributes(self, data):
        '''
        Set attribute for the object; implemend the __init__
        '''
        if not data:
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if snake_key in self.REFS:
                if type(data[key]) == str:
                    setattr(self, snake_key+'_id', data[key])
                elif (type(data[key] is dict)) and ('_id' in data[key]):
                    setattr(self, snake_key, data[key])
                    setattr(self, snake_key+'_id', data[key]['_id'])
            else:
                if snake_key in self.ATTRIBUTES:
                    setattr(self, snake_key, data[key])

    def __repr__(self, list_of_keys):
        string = f'\n{self.__class__.__name__}:\n'
        for each_k in list_of_keys:
            val = getattr(self, each_k,'')
            string += (str(each_k) + ": " + str(val) + '; ')
        return string

    def to_json(self):
        '''
        Convert the current object to json format, return the json format
        '''
        return {Utils.to_camel_case(key) : getattr(self, key)
         for key in self.ATTRIBUTES if getattr(self, key, None) != None}

    def save(self):
        '''
        Update data of the object in server, if the object has not in server yet,
        create a new instance and put the object on
        '''
        if not getattr(self, '_id', ''):
            new_data = self.db_service.post(f'/{self.name_of_class}', self.to_json())
            if new_data and '_id' in new_data:
                self.set_attributes(new_data)
        else:
            updated_data = self.db_service.put(f'/{self.name_of_class}/{self._id}', self.to_json())
            if updated_data and '_id' in updated_data:
                self.set_attributes(updated_data)

    @classmethod
    def create(cls, data=None):
        '''
        Class method; Update data of the object in server, if the object has not in server yet,
         create a new instance and put the object on
        Parameter:
            data: a dictionary or equivilant data type with key,value organisation of that can be
             used to create the object
        '''
        new_holder = cls(data)
        new_holder.save()
        return new_holder

    @classmethod
    def find(cls, filter_ = None, offset=0, limit=1000, order_by='', output = 'DataFrame'):
        '''
        Get maximum 1000 values that match the condition of the class and the filter condition
        Parameter:
         output: kind of multi-value class to holder the result. the default is 'DataFrame'
         filter: the filter condition for fitlering result. the default is {} (no filter)
        Return: result in corresponding output type, each single item is in current object type
        '''
        filter_params = Utils.build_filter_params(filter_, offset, limit, order_by)
        class_name_plural = Utils.to_camel_case(cls.name_of_class, joining='-')
        from_server = cls.db_service.get(f'/{cls.name_of_class}', query_params=filter_params)
        try:
            rows = Utils.output_form(cls, from_server[class_name_plural], output)
            total = from_server['totalNumber']
            return rows, total
        except:
            return [], 0

    @classmethod
    def find_all(cls, filter_ = None, output = 'DataFrame'):
        '''
        Get all values that match the condition of the class and the filter condition
        Parameter:
         output: kind of multi-value class to holder the result. the default is 'DataFrame'
         filter: the filter condition for fitlering result. the default is {} (no filter)
        Return: result in corresponding output type, each single item is in current object type
        '''
        limit = 5000
        rows, total_number = cls.find(filter_, limit=limit, output=output)
        if total_number <= limit:
            return rows, total_number

        steps = (total_number // limit) + 1
        for i in range(1, steps):
            offset = i * limit
            next_rows, _ = cls.find(filter_, offset=offset, limit=limit, output=output)
            rows = Utils.concatenate_output(rows, next_rows)
        
        return (rows, total_number)

    @classmethod
    def find_by_id(cls, the_id):
        '''
        Get the value from server that match the id
        Parameter:
         the_id: id in query
        Return: an object in current type that includes data type for object
        '''
        from_server = cls.db_service.get(f'/{cls.name_of_class}/{the_id}')
        return cls(from_server)

    @classmethod
    def find_one(cls, filter_= None):
        '''
        Get the first value of the class that match the condition filter
        Parameter:
            output: kind of multi-value class to holder the result. the default is 'DataFrame'
            filter: the filter condition for fitlering result. the default is {} (no filter)
        Return: result in current object type
        '''
        filter_params = Utils.build_filter_params(filter_)
        name_of_class_camel = Utils.to_camel_case(cls.name_of_class,joining='-')
        from_server = cls.db_service.get(f'/{cls.name_of_class}', query_params=filter_params)
        try:
            from_server = from_server[f'{name_of_class_camel}']
            from_server = from_server[0]
        except:
            return None
        return cls(from_server)

    @classmethod
    def delete_by_id(cls, the_id):
        '''
        Delete the value in server that match the id
        Parameter:
            the_id: id in query
        '''
        return cls.db_service.delete(f'/{cls.name_of_class}/{the_id}')
