from hyde.expressions import Visitor

class ASTPrinter(Visitor):
    def generate(self, expr):
        return self.visit(expr)

    def print(self, expr):
        print(self.generate(expr))

    def visit_binary(self, binary):
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def visit_grouping(self, grouping):
        return self.parenthesize('group', grouping.expression)

    def visit_literal(self, literal):
        if literal.value == None:
            return 'nil'

        return str(literal.value)

    def visit_unary(self, unary):
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def parenthesize(self, name, *exprs):
        text = f'({name}'

        for expr in exprs:
            text += ' '
            text += self.visit(expr)

        text += ')'

        return text