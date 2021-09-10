from os.path import exists
from pathvalidate import sanitize_filepath
from PyInquirer import Validator, ValidationError

class TitleValidator(Validator):
    def validate(self, document):
        if not document.text == sanitize_filepath(document.text):
            raise ValidationError(
                message='Illegal characters used',
                cursor_position=len(document.text))

        if exists(document.text):
            raise ValidationError(
                message='Folder already exists',
                cursor_position=len(document.text))

        if len(document.text) == 0:
            raise ValidationError(
                message='Project title can not be empty',
                cursor_position=len(document.text))
