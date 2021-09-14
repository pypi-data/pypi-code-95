class Expression:
    pass


class Assign(Expression):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Binary(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Call(Expression):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments


class Get(Expression):
    def __init__(self, object, name):
        self.object = object
        self.name = name


class Grouping(Expression):
    def __init__(self, expression):
        self.expression = expression


class Literal(Expression):
    def __init__(self, value):
        self.value = value


class Logical(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Set(Expression):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value


class This(Expression):
    def __init__(self, keyword):
        self.keyword = keyword


class Unary(Expression):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right


class Variable(Expression):
    def __init__(self, name):
        self.name = name


class Visitor:
    # Base methods to be overridden in child classes
    def visit_assign(self, assign):
        raise NotImplementedError('visit_assign')

    def visit_binary(self, binary):
        raise NotImplementedError('visit_binary')

    def visit_call(self, call):
        raise NotImplementedError('visit_call')

    def visit_get(self, get):
        raise NotImplementedError('visit_get')

    def visit_grouping(self, grouping):
        raise NotImplementedError('visit_grouping')

    def visit_literal(self, literal):
        raise NotImplementedError('visit_literal')

    def visit_logical(self, logical):
        raise NotImplementedError('visit_logical')

    def visit_set(self, set):
        raise NotImplementedError('visit_set')

    def visit_this(self, this):
        raise NotImplementedError('visit_this')

    def visit_unary(self, unary):
        raise NotImplementedError('visit_unary')

    def visit_variable(self, variable):
        raise NotImplementedError('visit_variable')

