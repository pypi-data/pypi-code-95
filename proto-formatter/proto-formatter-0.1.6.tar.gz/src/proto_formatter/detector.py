from proto_formatter.proto_structures import Comment
from proto_formatter.comment import CommentParser
from proto_formatter.constant import Constant
from proto_formatter.proto_structures import Position
from proto_formatter.util import remove_prefix, remove_suffix


class Detector(Constant):

    def get_top_comments(self, lines):
        comment_parser = CommentParser()
        comments_lines = comment_parser.pick_up_comment(lines)
        comments = comment_parser.parse(comments_lines)

        return comments

    def get_type(self, line):
        if self._is_syntax_line(line):
            return 'syntax'
        if self._is_package_line(line):
            return 'package'
        if self._is_option_line(line):
            return 'option'
        if self._is_import_line(line):
            return 'import'
        if self._is_message_object(line):
            return 'message'
        if self._is_enum_object(line):
            return 'enum'
        if self._is_service_object(line):
            return 'service'
        # if self._is_element_line(line):
        #     return 'element_field', comments
        if self._is_message_element(line):
            return 'message_element'
        if self._is_enum_element(line):
            return 'enum_element'
        if self._is_service_element(line):
            return 'service_element'
        if self._is_oneof_object(line):
            return 'oneof'

        return 'unknown'

    def is_object_ype(self, type):
        return type in ['message', 'enum', 'service', 'oneof']

    def _is_syntax_line(self, line):
        return line.replace(' ', '').startswith('syntax=')

    def _is_package_line(self, line):
        return line.strip().startswith('package ')

    def _is_option_line(self, line):
        return line.strip().startswith('option ')

    def _is_import_line(self, line):
        return line.strip().startswith('import ')

    def _is_object_start(self, line):
        if line.count(self.BRACE_LEFT) == 0:
            return False

        if line.count(self.SINGLE_COMMENT_SYMBOL) > 0:
            if line.index(self.BRACE_LEFT) > line.index(self.SINGLE_COMMENT_SYMBOL):
                return False

        if line.count(self.MULTIPLE_COMENT_START_SYMBOL) > 0:
            if line.index(self.BRACE_LEFT) > line.index(self.MULTIPLE_COMENT_START_SYMBOL):
                return False

        return True

    def _is_object_end(self, line):
        if line.count(self.BRACE_RIGHT) == 0:
            return False

        if line.count(self.SINGLE_COMMENT_SYMBOL) > 0:
            if line.index(self.BRACE_RIGHT) > line.index(self.SINGLE_COMMENT_SYMBOL):
                return False

        if line.count(self.MULTIPLE_COMENT_START_SYMBOL) > 0:
            if line.index(self.BRACE_RIGHT) > line.index(self.MULTIPLE_COMENT_START_SYMBOL):
                return False

        return True

    def _is_message_object(self, line):
        return line.strip().startswith('message ') and line.strip().count(self.BRACE_LEFT)

    def _is_oneof_object(self, line):
        return line.strip().startswith('oneof ') and line.strip().count(self.BRACE_LEFT)

    def _is_message_element(self, line):
        if not self._is_element_line(line):
            return False

        if self._is_map_element(line):
            return True

        parts = line.strip().split(self.EQUAL_SIGN)
        parts = [e for e in parts[0].strip().split(' ')]
        parts = list(filter(None, parts))

        if parts[0] == 'rpc':  # service element
            return False

        return len(parts) >= 2

    def _is_element_line(self, line):
        if line.count(self.SEMICOLON) == 0:
            return False

        if line.count(self.SINGLE_COMMENT_SYMBOL) > 0:
            if line.index(self.SEMICOLON) > line.index(self.SINGLE_COMMENT_SYMBOL):
                return False

        if line.count(self.MULTIPLE_COMENT_START_SYMBOL) > 0:
            if ine.index(self.SEMICOLON) > ine.index(self.MULTIPLE_COMENT_START_SYMBOL):
                return False

        if self._is_service_element_line(line):
            return True

        if self._is_map_element_line(line):
            return True

        return line.strip().count(self.SEMICOLON) > 0 and line.strip().count(self.EQUAL_SIGN) > 0

    def _is_service_element(self, line):
        if not self._is_element_line(line):
            return False

        # rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
        line = line.strip()
        return line.startswith('rpc ')

    def _is_service_element_line(self, line):
        # rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
        line = line.strip()
        return line.startswith('rpc ')

    def _is_map_element(self, line):
        if not self._is_element_line(line):
            return False

        # map<string, Project> projects = 3;
        line = line.strip().replace(' ', '')
        return line.startswith('map<')

    def _is_map_element_line(self, line):
        # map<string, Project> projects = 3;
        line = line.strip().replace(' ', '')
        return line.startswith('map<')

    def _is_enum_object(self, line):
        return line.strip().startswith('enum ') and line.strip().count(self.BRACE_LEFT)

    def _is_enum_element(self, line):
        if not self._is_element_line(line):
            return False

        parts = line.strip().split(self.EQUAL_SIGN)
        parts = [e for e in parts[0].strip().split(' ')]
        parts = list(filter(None, parts))

        return len(parts) == 1

    def _is_service_object(self, line):
        return line.strip().startswith('service ') and line.strip().count(self.BRACE_LEFT)
