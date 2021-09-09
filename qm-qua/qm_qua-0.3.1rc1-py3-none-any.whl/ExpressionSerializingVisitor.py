from qm.QuaNodeVisitor import QuaNodeVisitor


class ExpressionSerializingVisitor(QuaNodeVisitor):
    def __init__(self) -> None:
        self._out = ""
        super().__init__()

    def _default_visit(self, node):
        print("missing expression: " + node.DESCRIPTOR.full_name)
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_VarRefExpression(self, node):
        self._out = node.name if node.name else f"IO{node.ioNumber}"

    def visit_qm_grpc_qua_QuaProgram_ArrayVarRefExpression(self, node):
        self._out = node.name

    def visit_qm_grpc_qua_QuaProgram_ArrayCellRefExpression(self, node):
        var = ExpressionSerializingVisitor.serialize(node.arrayVar)
        index = ExpressionSerializingVisitor.serialize(node.index)
        self._out = f"{var}[{index}]"

    def visit_qm_grpc_qua_QuaProgram_LiteralExpression(self, node):
        self._out = node.value

    def visit_qm_grpc_qua_QuaProgram_AssignmentStatement_Target(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnalogProcessTarget_ScalarProcessTarget(
        self, node
    ):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnyScalarExpression(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_SaveStatement_Source(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_BinaryExpression(self, node):
        left = ExpressionSerializingVisitor.serialize(node.left)
        right = ExpressionSerializingVisitor.serialize(node.right)
        sop = node.op
        if sop == node.ADD:
            op = "+"
        elif sop == node.SUB:
            op = "-"
        elif sop == node.GT:
            op = ">"
        elif sop == node.LT:
            op = "<"
        elif sop == node.LET:
            op = "<="
        elif sop == node.GET:
            op = ">="
        elif sop == node.EQ:
            op = "=="
        elif sop == node.MULT:
            op = "*"
        elif sop == node.DIV:
            op = "/"
        elif sop == node.OR:
            op = "|"
        elif sop == node.AND:
            op = "&"
        elif sop == node.XOR:
            op = "^"
        elif sop == node.SHL:
            op = "<<"
        elif sop == node.SHR:
            op = ">>"
        else:
            raise Exception("Unsupported operator " + sop)
        self._out = f"{left}{op}{right}"

    @staticmethod
    def serialize(node) -> str:
        visitor = ExpressionSerializingVisitor()
        visitor.visit(node)
        return visitor._out
