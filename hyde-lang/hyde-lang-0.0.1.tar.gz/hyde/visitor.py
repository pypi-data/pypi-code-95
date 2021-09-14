from hyde.expressions import Visitor as ExpressionVisitor
from hyde.statements import Visitor as StatementVisitor


class Visitor(ExpressionVisitor, StatementVisitor):
    def visit(self, other):
        # This should never happen, but prevent Python errors from showing if it does
        if other is None:
            return

        visit_fn_name = f'visit_{type(other).__name__.lower()}'
        visit_fn = getattr(self, visit_fn_name)

        return visit_fn(other)