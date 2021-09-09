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
        def __call__(self, func):
            args = func.__code__.co_varnames[:func.__code__.co_argcount]
            self.retval = func(**{arg: globals()[arg] for arg in args})
            root = ast.parse(textwrap.dedent(inspect.getsource(func)))
            self.visit(root)
            return func
        def visit_Return(self, node):
            if type(node.value) == _ast.Name:
                globals()[node.value.id] = self.retval
            elif type(node.value) == _ast.Tuple:
                for elt, val in zip(node.value.elts, self.retval):
                    globals()[elt.id] = val
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