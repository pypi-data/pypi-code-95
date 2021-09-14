class Statement:
    pass


class Block(Statement):
    def __init__(self, statements):
        self.statements = statements


class ClassDef(Statement):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods


class Expression(Statement):
    def __init__(self, expression):
        self.expression = expression


class Function(Statement):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class IfStmt(Statement):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class Print(Statement):
    def __init__(self, expression):
        self.expression = expression


class ReturnStmt(Statement):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value


class Var(Statement):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer


class WhileStmt(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class Visitor:
    # Base methods to be overridden in child classes
    def visit_block(self, block):
        raise NotImplementedError('visit_block')

    def visit_classdef(self, classdef):
        raise NotImplementedError('visit_classdef')

    def visit_expression(self, expression):
        raise NotImplementedError('visit_expression')

    def visit_function(self, function):
        raise NotImplementedError('visit_function')

    def visit_ifstmt(self, ifstmt):
        raise NotImplementedError('visit_ifstmt')

    def visit_print(self, print):
        raise NotImplementedError('visit_print')

    def visit_returnstmt(self, returnstmt):
        raise NotImplementedError('visit_returnstmt')

    def visit_var(self, var):
        raise NotImplementedError('visit_var')

    def visit_whilestmt(self, whilestmt):
        raise NotImplementedError('visit_whilestmt')

