
from scoutregiment.scoutregiment_forest import *


def bash_(cmd):
    ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode != 0:
        logging.warning(ret.stderr)
    return ret.stdout

def bash(cmd):
    print(bash_(cmd).decode())

def _display(*colored_msg_list):
    _tab_width = option.scout_depth
    _tab_string = '  '*_tab_width
    msg = "  ".join(colored_msg_list)
    _msg = f"{_tab_string}{msg}"
    print(_msg)


class ScoutOption(object):
    _erwin = "erwin" # 查看成员名、文档中doctest可执行部分
    _hange = "hange" # 查看成员名、文档中所有内容
    _levi = "levi"
    _armin = "armin"
    def __init__(option):
        option.scout_depth_max = 2
        option.scout_leader = ScoutOption._levi
        option.scout_member_pattern = "^.*$"
        option.scout_depth = 0

option = ScoutOption()

scout_rich_console = rich.console.Console(style="magenta")

def _scout_doc(obj):
    if hasattr(obj, '__doc__') and obj.__doc__:
        docstring = doctest.script_from_examples(obj.__doc__)
        if option.scout_leader.lower() == ScoutOption._levi:
            docstring = '\n'.join([_ for _ in docstring.split("\n") if not _.startswith("#")])
        docstring_in_syntax = rich.syntax.Syntax(docstring, "python", theme='inkpot')
        scout_rich_console.print(docstring_in_syntax)
def _is_single_quota_doc_mark_line(line):
    return line.strip().startswith("'''") or line.strip().endswith("'''")
def _is_double_quota_doc_mark_line(line):
    return line.strip().startswith('"""') or line.strip().endswith('"""')
def _is_single_quota_one_line_doc(line):
    return line.strip().__len__() > 3 and line.strip().startswith("'''") and line.strip().endswith("'''")
def _is_double_quota_one_line_doc(line):
    return line.strip().__len__() > 3 and line.strip().startswith('"""') and line.strip().endswith('"""')
  

def _is_doc_mark_line(line):
    return _is_single_quota_doc_mark_line(line) or _is_double_quota_doc_mark_line(line)

def _is_one_line_doc(line):
    return _is_single_quota_one_line_doc(line) or _is_double_quota_one_line_doc(line)

def _scout_source(obj):
    if option.scout_depth > 1:
        return
    if option.scout_leader.lower() != ScoutOption._armin:
        return 
    drop = False
    lines = []
    for line in inspect.getsourcelines(obj)[0]:
        if _is_doc_mark_line(line) or _is_one_line_doc(line):
            if not _is_one_line_doc(line):
                drop = not drop
        elif not drop:
             lines.append(line)

    source_code = "".join(lines)
    source_code_in_syntax = rich.syntax.Syntax(source_code, "python", theme="inkpot")
    scout_rich_console.print(source_code_in_syntax)

def _scout_by_dir(obj):
    for _m in dir(obj):
        if _m.startswith("__"):
            pass
        elif re.findall(option.scout_member_pattern.strip(), _m):
            _scout_member(_m, getattr(obj, _m))
    

def _scout_member(_m, _o):
    if _o is None:
        return
    _display(colored(_m, "green", attrs=['bold']), colored(type(_o), 'blue'))
    if option.scout_depth >= option.scout_depth_max:
        return
    scout(_o)

def scout(obj):
    option.scout_depth
    
    if obj is None:
        return 
    _display(colored(obj, 'red'))
    option.scout_depth += 1
    _scout(obj)
    option.scout_depth -= 1

@functools.singledispatch
def _scout(obj):
    _scout_by_dir(obj)
    _scout_doc(obj)
    _scout_source(obj)
    
@_scout.register(types.FunctionType)
@_scout.register(types.MethodType)
def _(obj):
    _scout_doc(obj)
    _scout_source(obj)
@_scout.register(type)
def _(obj):
    _scout_by_dir(obj)
    _scout_doc(obj)
    _scout_source(obj)

@_scout.register(types.ModuleType)
def _(obj):
    _scout_by_dir(obj)
    _scout_doc(obj)
    _scout_source(obj)

@_scout.register(property)
def _(obj):
    _display(f"property")


# # option.scout_leader = ScoutOption._levi
# option.scout_depth = 3
# option.scout_member_pattern = """^[abcdefgs].+"""
# scout(doctest.argparse.HelpFormatter)