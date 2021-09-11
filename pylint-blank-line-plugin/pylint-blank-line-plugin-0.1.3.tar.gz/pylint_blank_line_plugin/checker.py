from pylint.checkers import BaseChecker
from pylint.interfaces import IRawChecker
from astroid.nodes.scoped_nodes import Module


class BlankLineChecker(BaseChecker):
    __implements__ = IRawChecker

    name = 'blank-line'
    priority = -100
    msgs = {
        'C0002': (
            'Wrong blank line.',
            'wrong-blank-line',
            'Methods should be separated from class definition by blank line. Return statement should be separated '
            'from other code by blank line if it is not first statement after indentation.'
        ),
        'C0003': (
            'Need a blank line.',
            'need-blank-line',
            'Methods should be separated from class definition by blank line. Return statement should be separated '
            'from other code by blank line if it is not first statement after indentation.'
        ),
    }

    def process_module(self, node: Module):
        # pylint: disable=too-many-branches,too-many-statements

        with node.stream() as stream:
            first_line = None
            second_line = None
            third_line = None
            for lineno, line in enumerate(stream):
                line_str = line.decode('utf-8').replace('\n', '')
                if lineno == 0:
                    first_line = line_str
                elif lineno == 1:
                    second_line = line_str
                elif lineno == 2:
                    third_line = line_str
                else:
                    first_line = second_line
                    second_line = third_line
                    third_line = line_str

                if second_line is None or third_line is None:
                    continue

                ret_stmt_second_line = (
                        second_line.strip().startswith('return ')
                        or second_line.strip().startswith('return\n')
                        or second_line.strip().startswith('yield ')
                        or second_line.strip().startswith('yield\n')
                        or second_line.strip().startswith('raise ')
                        or second_line.strip().startswith('raise\n')
                        or second_line.strip().startswith('break\n')
                        or second_line.strip().startswith('continue\n')
                )
                if ret_stmt_second_line and third_line != '':
                    second_line_copy = second_line
                    char = second_line_copy[0]
                    i = 0
                    while char == ' ':
                        second_line_copy = second_line_copy[1:]
                        char = second_line_copy[0]
                        i += 1

                    try:
                        if third_line[i] != ' ':
                            self.add_message('need-blank-line', line=lineno + 1)
                    except IndexError:
                        pass

                ret_stmt_third_line = (
                    third_line.strip().startswith('return ')
                    or third_line.strip().startswith('return\n')
                    or third_line.strip().startswith('yield ')
                    or third_line.strip().startswith('yield\n')
                    or third_line.strip().startswith('raise ')
                    or third_line.strip().startswith('raise\n')
                    or third_line.strip().startswith('break\n')
                    or third_line.strip().startswith('continue\n')
                )

                if ret_stmt_third_line:
                    if second_line.strip() == '':
                        if first_line.strip() == '':
                            self.add_message('wrong-blank-line', line=lineno)

                            continue

                        first_line_copy = first_line
                        char = first_line_copy[0]
                        i = 0
                        while char == ' ':
                            first_line_copy = first_line_copy[1:]
                            char = first_line_copy[0]
                            i += 1

                        try:
                            if third_line[i] == ' ':
                                self.add_message('wrong-blank-line', line=lineno)
                        except IndexError:
                            pass
                    else:
                        second_line_copy = second_line
                        char = second_line_copy[0]
                        i = 0
                        while char == ' ':
                            second_line_copy = second_line_copy[1:]
                            char = second_line_copy[0]
                            i += 1

                        if third_line[i + 1] != ' ':
                            self.add_message('need-blank-line', line=lineno + 1)
