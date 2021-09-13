from manparams.error import ParamError, find_in_code, find_in_tree


def test_print_param_error_displays_all_info():
    err = ParamError('param', "toto")
    display = str(err)
    assert "param" in display
    assert "toto" in display


def test_find_in_code_parses_all_raised_errors():
    code = b"""from bla import tutu
from manparams import *

raise ParamError('PARAM0', 'error message0')


def myfunc():
    raise ParamError('PARAM1', 'error message1')


class Toto:
    def __init__(self):
        self.voila = 'done'

    def mymethod(self):
        raise ParamError('PARAM2', 'error message2')


for i in range(10):
    raise ParamError('PARAM3', 'error message3')

try:
    a = 1
except ParamError as err:  # not supposed to be parsed
    print(err)

try:
    a = 1
except ParamError as err:
    print(err)
    raise  # this one is supposed to be parsed

try:
    a = 1
except UserWarning as err:
    raise ParamError('PARAM4', 'error message4' + str(err)) from err

raise ParamError('PARAM5', 'error message5')  # just to check that we parse all the file
"""

    errors = find_in_code(code)

    assert len(errors) == 6
    assert [f'PARAM{i:d}' for i in range(6)] == sorted(err.pname for err in errors)


def test_find_in_code_avoid_other_errors():
    for code in [b"raise UserWarning('ParamError')\n",
                 b"raise TotoError(pname='PARAM', msg='message')\n"]:
        errors = find_in_code(code)

        assert len(errors) == 0


def test_find_in_code_parses_correct_attributes_when_defined_in_constructor():
    for code in [b"raise ParamError('PARAM', 'message')\n",
                 b"raise ParamError('PARAM', msg='message')\n",
                 b"raise ParamError(pname='PARAM', msg='message')\n",
                 b"raise ParamError(msg='message', pname='PARAM')\n"]:
        error, = find_in_code(code)

        assert error.pname == 'PARAM'
        assert error.msg == 'message'


def test_find_in_code_parses_correct_attributes_when_assigned_to_str_variables_before():
    preamble = b"""from manparams import *

pname_prefix = "PARAM"
pname = "PARAM.P0"
error_msg = "message"
eid = 10
"""

    for code in [b"raise ParamError(pname, error_msg)\n",
                 b"raise ParamError(f'{pname}', f'{error_msg}')\n",
                 b"raise ParamError(f'{pname_prefix}.P0', f'{error_msg} with more')\n",
                 b"raise ParamError(f'{pname_prefix}.P0', f'{error_msg} with number {eid:d}')\n"][-1:]:
        error, = find_in_code(preamble + code)

        assert error.pname == 'PARAM.P0'
        assert error.msg.startswith('message')


def test_find_in_code_parses_attributes_as_x_if_undefined():
    preamble = b"""from manparams import *

pname_prefix = "PARAM"
pname = "PARAM.P0"
error_msg = "message"
eid = 10
"""

    for code in [b"raise ParamError(param1, error_msg1)\n",
                 b"raise ParamError(f'{param1}', f'{error_msg1}')\n",
                 b"raise ParamError(f'{pname_prefix1}.P{eid:d}', f'{error_msg1} with number {eid:d}')\n"]:
        error, = find_in_code(preamble + code)

        assert "XXXXXXX" in error.pname
        assert "XXXXXXX" in error.msg


def test_find_in_code_avoids_full_duplicates():
    code = b"""from manparams import *

raise ParamError('PARAM0', 'message0')
raise ParamError('PARAM0', 'message1')
raise ParamError('PARAM0', 'message0')  # duplicate
raise ParamError('PARAM1', 'message1')
"""
    errors = find_in_code(code)

    assert len(errors) == 3


def test_find_in_code_sorts_error_by_pname():
    code = b"""from manparams import *

raise ParamError('PARAM2', 'message2')
raise ParamError('PARAM0', 'message2')
raise ParamError('PARAM0', 'message1')
raise ParamError('PARAM1', 'message1')
"""
    errors = find_in_code(code)

    sorted_errors = sorted(errors, key=lambda item: (item.pname, item.msg))

    assert errors == sorted_errors


def test_find_in_code_fails_in_complex_cases():
    code = b"""from bla import tutu
from manparams import *

err = ParamError('PARAM0', 'error message0')
raise err
"""

    errors = find_in_code(code)

    assert len(errors) == 0


def test_find_in_tree_parses_all_python_files_in_tree(tmp_path):
    # create dummy package
    for i in range(5):
        pth = tmp_path / f"myscript_{i:03d}.py"
        pth.write_text(f"""from manparams import *

raise ParamError('PARAM{i:d}', 'message{i:d}')
""")

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    for i in range(5):
        pth = sub_dir / f"myscript_{i:03d}.py"
        pth.write_text(f"""from manparams import *

raise ParamError('PARAM.sub{i:d}', 'message_sub{i:d}')
""")

    # test parsing
    errors = find_in_tree(tmp_path)

    assert len(errors) == 10


def test_find_in_tree_ignores_non_python_files(tmp_path):
    # create dummy package
    for i in range(5):
        pth = tmp_path / f"myscript_{i:03d}.py"
        pth.write_text(f"""from manparams import *

raise ParamError('PARAM{i:d}', 'message{i:d}')
""")

    for i in range(5):
        pth = tmp_path / f"myscript_{i:03d}.txt"  # non python file
        pth.write_text(f"""from manparams import *

raise ParamError('PARAM.txt{i:d}', 'message_txt{i:d}')
""")

    # test parsing
    errors = find_in_tree(tmp_path)

    assert len(errors) == 5
