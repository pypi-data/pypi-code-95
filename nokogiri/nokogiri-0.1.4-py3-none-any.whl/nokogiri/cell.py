#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    assert get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    IS_JUPYTER = True
except:
    IS_JUPYTER = False
if IS_JUPYTER:
    import inspect
    import ast
    import _ast
    import textwrap
    class cell(ast.NodeVisitor):
        def __init__(self, g=globals(), *args, **kwargs):
            self.g = g
            super().__init__(*args, **kwargs)
        def __call__(self, func):
            args = func.__code__.co_varnames[:func.__code__.co_argcount]
            self.retval = func(**{arg: self.g[arg] for arg in args})
            root = ast.parse(textwrap.dedent(inspect.getsource(func)))
            self.visit(root)
            return func
        def visit_Return(self, node):
            if type(node.value) == _ast.Name:
                self.g[node.value.id] = self.retval
            elif type(node.value) == _ast.Tuple:
                for elt, val in zip(node.value.elts, self.retval):
                    self.g[elt.id] = val
            self.generic_visit(node)
    if __name__ == '__main__':
        A = 1
        B = 2
        @cell()
        def func(A, B):
            C = A+B
            D = A*B
            return C, D
        print(C, D)
else:
    cell = lambda: lambda func: func