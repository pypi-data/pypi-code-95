import re
from dataclasses import field, dataclass
from typing import List
from .class_ import Class

@dataclass
class Namespace:
    Classes: List[Class] = field(default_factory=list)
    Name: str = ""
    Code: str = ""

    def create_tree(self):
        _class_code = ''
        open_brace_count = 0
        close_brace_count = 0
        for char in self.Code:
            if char == '{':
                open_brace_count += 1
            if char == '}':
                close_brace_count += 1
            _class_code += char
            if close_brace_count == open_brace_count and close_brace_count > 0:
                class_match = re.search(
                    r"[^//](public|internal|)\s*class\s*([a-zA-Z]*)", _class_code)
                if class_match is None:
                    continue
                self.Classes.append(
                    Class(Code=_class_code, Name=class_match.group(2)).create_tree())
                open_brace_count = 0
                close_brace_count = 0
                _class_code = ''
        return self

    def print_tree(self):
        if self.Name == '':
            return
        print(self.Name)
        for c in self.Classes:
            for attribute in c.Attributes:
                print(' [' + attribute.Name + ']')
            print(' ' + c.Name)
            for method in c.Methods:
                for attribute in method.Attributes:
                    print(' [' + attribute.Name + ']')
                print('     ' + method.Access_modifiers +
                      method.Return_type + method.Name)
            for prop in c.Propeties:
                print('         ' + prop.Access_modifiers +
                      prop.Return_type + prop.Name)
