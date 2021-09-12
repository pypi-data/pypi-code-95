import datetime
import sys
import traceback
import types
from typing import Optional

from qm import _Program, version
from qm.QuaNodeVisitor import QuaNodeVisitor
from qm.QuaSerializingVisitor import QuaSerializingVisitor
from qm.pb.inc_qua_config_pb2 import QuaConfig
from qm.pb.inc_qua_pb2 import QuaProgram
from qm.program import load_config
from qm.program.ConfigBuilder import convert_msg_to_config


def generate_qua_script(prog: _Program, config: Optional[dict] = None) -> str:
    if prog.is_in_scope():
        raise RuntimeError("Can not generate script inside the qua program scope")
    proto_config = None
    if config is not None:
        proto_config = load_config(config)
    proto_prog = prog.build(QuaConfig())
    return _generate_qua_script_pb(proto_prog, proto_config)


def _generate_qua_script_pb(proto_prog, proto_config):
    new_config = None
    if proto_config is not None:
        new_config = convert_msg_to_config(proto_config)
    extra_info = ""
    serialized_program = ""
    try:
        visitor = QuaSerializingVisitor()
        visitor.visit(proto_prog)
        serialized_program = visitor.out()

        extra_info = _validate_program(proto_prog, serialized_program)
    except Exception as e:
        trace = traceback.format_exception(*sys.exc_info())
        extra_info = extra_info + _error_string(e, trace)

    return f"""
# Single QUA script generated at {datetime.datetime.now()}
# QUA library version: {version.__version__}

{serialized_program}

config = {new_config}

{extra_info if extra_info else ""}
"""


def _validate_program(old_prog, serialized_program: str) -> Optional[str]:
    generated_mod = types.ModuleType("gen")
    exec(serialized_program, generated_mod.__dict__)
    new_prog = generated_mod.prog.build(QuaConfig())

    new_prog_str = _program_string(new_prog)
    old_prog_str = _program_string(old_prog)

    if new_prog_str != old_prog_str:
        return f"""
####     SERIALIZATION WAS NOT COMPLETE     ####
#
#  Original   {old_prog_str}
#  Serialized {new_prog_str}
#
################################################
        """

    return None


def _error_string(e: Exception, trace) -> str:
    return f"""
    ####     SERIALIZATION VALIDATION ERROR     ####
    #
    #  {str(e)}
    #
    # Trace:
    #   {str(trace)}
    #
    ################################################
            """


def _program_string(prog) -> str:
    """
    Will create a canonized string representation of the program
    """
    copy = QuaProgram()
    copy.CopyFrom(prog)
    strip_location_visitor = _StripLocationVisitor()
    strip_location_visitor.visit(copy)
    string = str(copy)
    string = string.replace("\n", "")
    return string


class _StripLocationVisitor(QuaNodeVisitor):
    """
    Go over all nodes and if they have a location property, we strip it
    """

    def _default_enter(self, node):
        if hasattr(node, "loc"):
            node.loc = "stripped"
        return True

    @staticmethod
    def strip(node):
        _StripLocationVisitor().visit(node)
