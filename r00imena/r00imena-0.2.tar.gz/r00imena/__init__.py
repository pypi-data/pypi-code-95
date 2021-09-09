import os
import codecs
import random


class Imena:
    """ Генерация Фамилии, Имени, Отчества!"""
    FIRSTNAME = 'firstname'
    LASTNAME = 'lastname'
    OTCH = 'otch'

    def __init__(self, gender, country):
        """
        :param gender: 'male', 'female'
        :param country: 'rus', 'ukr', 'eng'
        """
        self.gender = gender
        self.country = country
        self.firstname = None
        self.lastname = None
        self.otch = None
        self.generate()

    def generate(self):
        arr = [Imena.FIRSTNAME, Imena.LASTNAME, Imena.OTCH]
        if self.country == 'eng': arr.pop()
        for prefix in arr:
            filename = prefix + '_' + self.gender + '_' + self.country + '.txt'
            filepath = os.path.join(os.path.dirname(__file__), filename)
            with codecs.open(filepath, "r", 'utf_8_sig') as f:
                line = random.choice(f.read().splitlines())
                setattr(self, prefix, line)

    @staticmethod
    def version():
        return '3.5'


if __name__ == '__main__':
    imena = Imena('male', 'eng')
    print(imena.firstname)
    print(imena.lastname)
    print(imena.otch)

    imena.generate()

    print(imena.firstname)
    print(imena.lastname)
    print(imena.otch)
