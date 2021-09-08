
import re
from dataclasses import dataclass, field
from typing import List
from . import Attribute
from . import Property
from . import Method


@dataclass
class Class:
    Name: str = ""
    Code: str = ""
    Propeties: List[Property] = field(default_factory=list)
    Methods: List[Method] = field(default_factory=list)
    Attributes: List[Attribute] = field(default_factory=list)

    def create_tree(self):
        open_brace_attribute = 0
        close_brace_attribute = 0
        open_brace_class = 0
        close_brace_class = 0
        attribute_name = ''
        code = ''
        for char in self.Code:
            if char == '[':
                open_brace_attribute += 1
            elif char == ']':
                close_brace_attribute += 1
                is_attribute_close = open_brace_attribute == close_brace_attribute and close_brace_attribute > 0
                if is_attribute_close:
                    if not is_class_open:
                        self.Attributes.append(
                            Attribute(Name=attribute_name, Is_class=True))
                    attribute_name = ''
                    open_brace_attribute = 0
                    close_brace_attribute = 0
            elif char == '{':
                open_brace_class += 1
            elif char == '}':
                close_brace_class += 1
                if abs(open_brace_class - close_brace_class) == 1:
                    code += char
                    if code[0] == '{':
                        code = code[1:]
                    property_match = re.search(
                        r'(public|internal|private|protected)\s*([a-zA-Z]*)\s*([a-zA-Z_<>]*)\s([a-zA-Z_0-9]*)\s*\s*{([\s\S]*)}', code)

                    if property_match is not None:
                        self.Propeties.append(
                            Property(Access_modifiers=property_match.group(1),
                                     Is_static=property_match.group(2) == 'static',
                                     Return_type=property_match.group(3),
                                     Name=property_match.group(4),
                                     Return_values=re.findall(
                                         r'return\s*([\s\S]*?;\n)', code),
                                     Code=code
                                     ))

                    method_match = re.search(
                        r'(public|internal|private|protected)\s*(async|)\s*([a-zA-Z]*)\s*([a-zA-Z_0-9]*)\(([a-zA-Z.0-9 ,<>\n]*)\)([\s\S]*?return\s*([\s\S]*?);|)', code)

                    if method_match is not None:
                        self.Methods.append(
                            Method(Access_modifiers=method_match.group(1),
                                   Is_Async=method_match.group(2) == 'async',
                                   Return_type=method_match.group(3),
                                   Name=method_match.group(4),
                                   Parametrs=method_match.group(5),
                                   Return_value=method_match.group(7),
                                   Code=code).create_tree())
                    code = ''
                    continue

            is_attribute_open = open_brace_attribute > close_brace_attribute and (
                char != '[' and char != ']')
            is_class_open = open_brace_class > close_brace_class

            if is_attribute_open:
                attribute_name += char

            if is_class_open:
                code += char

        return self
