import uuid
from enum import Enum
from proto_formatter.detector import Detector
from proto_formatter.comment import CommentParser
from proto_formatter.constant import Constant
from proto_formatter.proto_structures import EnumElement
from proto_formatter.proto_structures import Import
from proto_formatter.proto_structures import Message
from proto_formatter.proto_structures import MessageElement
from proto_formatter.proto_structures import Option
from proto_formatter.proto_structures import Package
from proto_formatter.proto_structures import Position
from proto_formatter.proto_structures import ProtoEnum
from proto_formatter.proto_structures import Service
from proto_formatter.proto_structures import ServiceElement
from proto_formatter.proto_structures import Syntax
from proto_formatter.proto_structures import Oneof
from proto_formatter.proto_structures import OneofElement
from proto_formatter.protobuf import Protobuf
from proto_formatter.util import remove_prefix, remove_suffix


class ObjectParser(Constant):

    def __init__(self):
        self.objects = []
        self.objects_dict = {}

        self.left_brace_stack = []
        self.right_brace_stack = []

        self.obj = None
        self.current_obj = None

    @classmethod
    def _get_obj_name(cls, line):
        parts = line.strip().split(' ')
        parts = list(filter(None, parts))
        name = parts[1]
        return name

    @classmethod
    def parse_obj_field(cls, line, top_comments):
        raise NotImplementedError("Element parse not implemented.")

    def parse_and_add(self, proto_obj: Protobuf, lines, top_comment_list):
        self.parse(lines, top_comment_list, True)
        proto_obj.objects.append(self.obj)

    def parse(self, lines):
        top_comments = Detector().get_top_comments(lines)
        if len(lines) == 0:
            return

        first_line = lines[0]
        if Detector()._is_object_start(first_line):
            self.left_brace_stack.append(self.BRACE_LEFT)

        type = Detector().get_type(first_line)
        if 'message' == type or 'enum' == type or 'service' == type or 'oneof' == type:
            name = self._get_obj_name(first_line)
            top_comments = CommentParser.create_comment(first_line, top_comments)
            obj = self.new_obj(type, name, top_comments)
            self.objects_dict[obj.id] = obj

            if self.obj:
                self.current_obj.elements.append(obj)
                obj.parent_id = self.current_obj.id
            else:
                self.obj = obj
                obj.parent_id = None
            self.current_obj = obj  # used as a pointer

            lines.pop(0)
            return self.parse(lines)
        elif 'enum_element' == type or 'message_element' == type or 'service_element' == type or 'oneof' == type:
            element = self.parse_element(type, first_line, top_comments)
            self.current_obj.elements.append(element)

            lines.pop(0)
            return self.parse(lines)
        else:
            if Detector()._is_object_end(first_line):
                self.right_brace_stack.append(self.BRACE_RIGHT)
                if self.current_obj.parent_id is None:  # root node, finish a root level object parse
                    self.objects.append(self.current_obj)
                    self.obj = None  # finshed a object and all netested inner objects(if has) parse.
                else:
                    self.current_obj = self.objects_dict[self.current_obj.parent_id]

                lines.pop(0)
                return self.parse(lines)

    @classmethod
    def new_obj(cls, type, name, comments=[]):
        obj_class = {
            'enum': ProtoEnum,
            'message': Message,
            'service': Service,
            'oneof': Oneof
        }[type]

        obj = obj_class(name=name, elements=[], comments=comments)
        obj.id = uuid.uuid4().hex

        return obj

    @classmethod
    def parse_element(cls, type, line, top_comments=[]):
        parse_method = {
            'enum_element': cls.parse_enum_element,
            'message_element': cls.parse_message_element,
            'service_element': cls.parse_service_element
        }[type]

        return parse_method(line, top_comments=top_comments)

    @classmethod
    def parse_enum_element(cls, line, top_comments=[]):
        # BAGGAGE_TYPE_CARRY_ON = 1;
        line = line.strip()
        equal_sign_index = line.index(cls.EQUAL_SIGN)
        semicolon_index = line.index(cls.SEMICOLON)
        str_before_equqal_sign = line[:equal_sign_index]
        parts = str_before_equqal_sign.split(' ')
        parts = list(filter(None, parts))
        value = line[equal_sign_index + 1:semicolon_index].strip().replace('"', "").replace("'", "")
        comments = CommentParser.create_comment(line, top_comments)
        return EnumElement(name=parts[0], number=value, comments=comments)

    @classmethod
    def parse_message_element(self, line, top_comments=[]):
        # common.RequestContext  request_context = 1;
        # map<string, Project> projects = 3;
        if 'map<' in line:
            return self.make_map_element(line, top_comments)

        line = line.strip()
        equal_sign_index = line.index(self.EQUAL_SIGN)
        semicolon_index = line.index(self.SEMICOLON)
        str_before_equqal_sign = line[:equal_sign_index]
        parts = str_before_equqal_sign.split(' ')
        parts = list(filter(None, parts))
        value = line[equal_sign_index + 1:semicolon_index].strip().replace('"', "").replace("'", "")
        comments = CommentParser.create_comment(line, top_comments)
        if len(parts) == 2:
            return MessageElement(label=None, type=parts[0], name=parts[1], number=value, comments=comments)
        if len(parts) == 3:
            return MessageElement(label=parts[0], type=parts[1], name=parts[2], number=value, comments=comments)

        return None

    @classmethod
    def make_map_element(self, line, top_comments=[]):
        # map<string, Project> projects = 3;
        right_bracket_index = line.index(self.ANGLE_BRACKET_RIGHT)
        equal_sign_index = line.index(self.EQUAL_SIGN)
        semicolon_index = line.index(self.SEMICOLON)
        type = line[:right_bracket_index + 1]
        type = type.strip().replace(' ', '')
        type_parts = type.split(',')
        type = ', '.join(type_parts)
        name = line[right_bracket_index + 1:equal_sign_index]
        name = name.strip()
        number = line[equal_sign_index + 1:semicolon_index]
        number = number.strip()
        comments = CommentParser.create_comment(line, top_comments)

        return MessageElement(label=None, type=type, name=name, number=number, comments=comments)

    @classmethod
    def parse_service_element(cls, line, top_comments=[]):
        # rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
        line = line.strip().replace('(', '')
        line = line.replace(')', '')

        semicolon_index = line.index(cls.SEMICOLON)
        str_before_semicolon = line[:semicolon_index]
        parts = str_before_semicolon.split(' ')
        parts = list(filter(None, parts))
        comments = CommentParser.create_comment(line, top_comments)

        return ServiceElement(label=parts[0], name=parts[1], request=parts[2], response=parts[4], comments=comments)
