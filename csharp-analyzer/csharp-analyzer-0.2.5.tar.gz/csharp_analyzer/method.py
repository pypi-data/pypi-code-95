from dataclasses import dataclass, field
from typing import List
from .attribute import Attribute

@dataclass
class Method:
    Name: str = ''
    Code: str = ''
    Access_modifiers: str = ''
    Return_type: str = ''
    Is_static: bool = False
    Is_Async: bool = False
    Attributes: List[Attribute] = field(default_factory=list)
    Parametrs: List[str] = field(default_factory=list)
    Return_value: str = ''

    def create_tree(self):
        open_method_count = 0
        close_method_count = 0
        open_attribute_count = 0
        close_attribute_count = 0
        _attrubute_name = ''
        _method_code = ''
        for char in self.Code:
            if char == '[':
                open_attribute_count += 1
            if char == ']':
                close_attribute_count += 1
                if open_attribute_count == close_attribute_count and not open_method_count > close_method_count:
                    self.Attributes.append(
                        Attribute(Name=_attrubute_name, Is_method=True))
                    open_attribute_count = 0
                    close_attribute_count = 0
                    _attrubute_name = ''
                    continue
            if char == '{':
                open_method_count += 1
            if char == '}':
                close_method_count += 1
                if close_method_count == open_method_count:
                    open_method_count = 0
                    close_method_count = 0

            is_attribute_open = open_attribute_count > close_attribute_count
            is_method_open = open_method_count > close_method_count
            if is_attribute_open and not is_method_open and (char != '[' and char != ']'):
                _attrubute_name += char
            if is_method_open:
                _method_code += char

        return self
