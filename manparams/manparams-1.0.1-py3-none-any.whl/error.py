"""
Simple error class for problems with params with tools to find them in code.
"""
import ast


class ParamError(Exception):
    """Base class for all error relevant for parameters
    """

    def __init__(self, pname, msg):
        self.pname = pname
        self.msg = msg

    def __str__(self):
        return f"[{self.pname}]: {self.msg}"


def find_in_code(code):
    """Parse code to find all ParamError

    Args:
        code (bytes): code to parse (not executed)

    Returns:
        (List[ParamError]): list of all ParamError sorted by param name
    """
    visitor = ErrorVisitor()
    pt = ast.parse(code)
    visitor.visit(pt)

    return [ParamError(*args) for args in visitor.param_errors()]


def find_in_tree(fld):
    """Parse file tree to find all ParamError

    Args:
        fld (Path): root directory to explore. All *.py file will be parsed
                    but not executed.

    Returns:
        (List[ParamError]): list of all ParamError sorted by param name
    """
    visitor = ErrorVisitor()
    for pth in fld.rglob('*.py'):
        pt = ast.parse(pth.read_bytes(), pth.name)
        visitor.visit(pt)

    return [ParamError(*args) for args in visitor.param_errors()]


class ErrorVisitor(ast.NodeVisitor):
    """Visitor class to parse files and get code and message of all raised ParamError object
    """

    def __init__(self):
        super().__init__()

        self._assign = {}
        self._param_errs = set()

    def fmt_str_node(self, node):
        if isinstance(node, ast.Name):
            try:
                return self._assign[node.id]
            except (KeyError, AttributeError):
                pass
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.JoinedStr):
            return ''.join([self.fmt_str_node(v) for v in node.values])
        elif isinstance(node, ast.FormattedValue):
            try:
                return str(self._assign[node.value.id])
            except (KeyError, AttributeError):
                pass
        return "XXXXXXX"

    def visit_Assign(self, node):
        val = self.fmt_str_node(node.value)
        for name in node.targets:
            try:
                self._assign[name.id] = val
            except AttributeError:
                pass

    def visit_Raise(self, node):
        exception = node.exc
        if hasattr(exception, 'func') and exception.func.id == 'ParamError':
            err_descr = {}
            for key, val in zip(['pname', 'msg'], exception.args):
                err_descr[key] = self.fmt_str_node(val)

            for kwd in exception.keywords:
                err_descr[kwd.arg] = self.fmt_str_node(kwd.value)

            self._param_errs.add((err_descr['pname'], err_descr['msg']))

    def param_errors(self):
        return sorted(self._param_errs)
