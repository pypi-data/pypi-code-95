from wtforms import Form, fields
from wtforms.fields.html5 import DateField


class BaseModelForm(Form):
    _fields = [] # a list of all fields to make it
                 # easier to extract arguments from request


class NullDateTimeField(fields.DateTimeField):
    """A nullable DateTimeField. Returns None for empty value.
    
    Renders separate date and time fields for better browser support.
    """
    def process_data(self, value):
        super().process_data(value)
        if self.data == '':
            self.data = None


class NullDateField(DateField):
    """A nullable DateField. Returns None for empty value.

    WTForm's DateField returns empty string, but Tortoise-ORM
    expects a None value
    """ 
    def process_data(self, value):
        super().process_data(value)
        if self.data == '':
            self.data = None