from hyde.hyde_instance import HydeInstance, HydeInstanceError
from hyde.environment import Environment
from hyde.environment import RuntimeError as EnvironmentRuntimeError
from hyde.errors import BaseError, Return
from hyde.globals import Globals
from hyde.hyde_callable import HydeCallable
from hyde.hyde_class import HydeClass
from hyde.hyde_function import HydeFunction
from hyde.token import TokenType
from hyde.visitor import Visitor


class InterpreterError(BaseError):
    pass


class InterpreterRuntimeError(BaseError):
    pass


class Interpreter(Visitor):
    def __init__(self, runtime):
        self.runtime     = runtime
        self.globals     = Environment()
        self.environment = self.globals
        self.locals      = {}

        Globals.define(self.globals)

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except InterpreterError as ex:
            self.runtime.error(ex)
        except (HydeInstanceError, InterpreterRuntimeError, EnvironmentRuntimeError) as ex:
            self.runtime.runtime_error(ex)

    def execute(self, stmt):
        return self.visit(stmt)

    def execute_block(self, statements, environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    # Visit Expressions
    def visit_assign(self, expr):
        value = self.visit(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_binary(self, expr):
        left  = self.visit(expr.left)
        right = self.visit(expr.right)
        operator = expr.operator

        if operator.type == TokenType.GREATER:
            self.check_number_operands(operator, left, right)
            return float(left) > float(right)
        elif operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(operator, left, right)
            return float(left) >= float(right)
        elif operator.type == TokenType.LESS:
            self.check_number_operands(operator, left, right)
            return float(left) < float(right)
        elif operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(operator, left, right)
            return float(left) <= float(right)
        elif operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        elif operator.type == TokenType.MINUS:
            self.check_number_operands(operator, left, right)
            return float(left) - float(right)
        elif operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)

            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

            self.runtime_error(operator, 'Operands must be two numbers or two strings.')
        elif operator.type == TokenType.SLASH:
            self.check_number_operands(operator, left, right)
            self.guard_division_by_zero(operator, right)
            return float(left) / float(right)
        elif operator.type == TokenType.STAR:
            self.check_number_operands(operator, left, right)
            return float(left) * float(right)

    def visit_call(self, expr):
        callee = self.visit(expr.callee)

        if not isinstance(callee, HydeCallable):
            self.error(expr.paren, 'Can only call functions and classes.')

        arguments = []

        for argument in expr.arguments:
            arguments.append(self.visit(argument))


        if len(arguments) != callee.arity:
            self.error(expr.paren, f'Expected {callee.arity} arguments but got {len(arguments)}')

        return callee.call(self, arguments)

    def visit_get(self, expr):
        object = self.visit(expr.object)

        if isinstance(object, HydeInstance):
            return object.get(expr.name)

        raise InterpreterRuntimeError(expr.name, 'Only instances have properties.')

    def visit_grouping(self, expr):
        return self.visit(expr.expression)

    def visit_literal(self, expr):
        return expr.value
    
    def visit_logical(self, expr):
        left = self.visit(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.visit(expr.right)

    def visit_set(self, expr):
        object = self.visit(expr.object)

        if not isinstance(object, HydeInstance):
            raise InterpreterRuntimeError(expr.name, 'Only instances have fields.')

        value = self.visit(expr.value)
        object.set(expr.name, value)

        return value

    def visit_this(self, expr):
        return self.look_up_variable(expr.keyword, expr)

    def visit_unary(self, expr):
        right = self.visit(expr.right)

        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return float(right) * -1

    def visit_variable(self, expr):
        return self.look_up_variable(expr.name, expr)

    # Visit Statements
    def visit_block(self, stmt):
        self.execute_block(stmt.statements, Environment(enclosing = self.environment))

    def visit_classdef(self, stmt):
        self.environment.define(stmt.name.lexeme, None)

        methods = {}
        for method in stmt.methods:
            function = HydeFunction(method, self.environment, method.name.lexeme == 'init')
            methods[method.name.lexeme] = function

        klass = HydeClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)

    def visit_expression(self, stmt):
        self.visit(stmt.expression)

    def visit_function(self, stmt):
        fn = HydeFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, fn)

    def visit_ifstmt(self, stmt):
        if self.is_truthy(self.visit(stmt.condition)):
            self.execute(stmt.then_branch)
        else:
            self.execute(stmt.else_branch)

    def visit_print(self, stmt):
        value = self.visit(stmt.expression)
        print(value)

    def visit_returnstmt(self, stmt):
        value = None

        if stmt.value is not None:
            value = self.visit(stmt.value)

        raise Return(value)

    def visit_whilestmt(self, stmt):
        while self.is_truthy(self.visit(stmt.condition)):
            self.execute(stmt.body)

    def visit_var(self, stmt):
        value = None
        
        if stmt.initializer is not None:
            value = self.visit(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    # Helpers
    def is_truthy(self, object):
        if object is None:
            return False
        
        if object in [True, False]:
            return object

        return True

    def is_equal(self, left, right):
        return left == right

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return

        self.runtime_error(operator, 'Operand must be a number.')

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return

        self.runtime_error(operator, 'Operands must be numbers.')

    def guard_division_by_zero(self, operator, right):
        if float(right) == 0:
            self.runtime_error(operator, "Can't divide by zero.")

    def look_up_variable(self, name, expr):
        distance = self.locals.get(expr)

        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def error(self, token, message):
        raise InterpreterError(token, message)

    def runtime_error(self, token, message):
        raise InterpreterRuntimeError(token, message)
