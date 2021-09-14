"""Generate type annotated python from SQL."""

from importlib.resources import read_text

import black
from lark import Lark, Transformer, UnexpectedToken
from jinja2 import Template, StrictUndefined


class SqlPyGenTransformer(Transformer):
    """Transform the parse tree for code generation."""

    CNAME = str
    MODULE_NAME = str

    def SQL_STRING(self, t):
        return t.strip().rstrip(";").strip()

    def type(self, ts):
        name, old_type = ts
        return ("types", {"name": name, "old_type": old_type})

    def module(self, ts):
        (name,) = ts
        return ("module", name)

    def pname_ptype(self, ts):
        pname, ptype = ts
        return {"name": pname, "type": ptype}

    def params(self, ts):
        return ("params", ts)

    def return_(self, ts):
        return ("return_", ts)

    def schema(self, ts):
        name, sql = ts
        return ("schemas", {"name": name, "sql": sql})

    def query(self, ts):
        name, sql = ts[0], ts[-1]
        params, return_ = [], []
        for typ, val in ts[1:-1]:
            if typ == "params":
                params = val
            elif typ == "return_":
                return_ = val
            else:
                raise ValueError(f"Unexpected child type: {typ=} {val=}")
        return (
            "queries",
            {"name": name, "params": params, "return_": return_, "sql": sql},
        )

    def import_stmt(self, ts):
        module, *names = ts
        return ("import_stmts", {"module": module, "names": names})

    def start(self, ts):
        ret = {
            "module": None,
            "import_stmts": [],
            "types": [],
            "schemas": [],
            "queries": [],
        }
        for grp, val in ts:
            if grp == "module":
                ret["module"] = val
            else:
                ret[grp].append(val)

        return ret


def get_parser() -> Lark:
    """Return the parser."""
    grammar = read_text("sqlpygen", "sqlpygen.lark")
    parser = Lark(grammar, parser="lalr")
    return parser


def get_template() -> Template:
    """Return the code generation template."""
    tpl_text = read_text("sqlpygen", "sqlpygen.jinja2")
    tpl_obj = Template(
        tpl_text, trim_blocks=True, lstrip_blocks=True, undefined=StrictUndefined
    )
    return tpl_obj


def generate(text: str) -> str:
    """Generate python from annotated sql."""
    parser = get_parser()
    transformer = SqlPyGenTransformer()
    template = get_template()

    try:
        parse_tree = parser.parse(text)
    except UnexpectedToken as e:
        line, col = e.line - 1, e.column - 1
        col_m1 = max(0, col)
        err_line = text.split("\n")[line]
        err_marker = "-" * col_m1 + "^"
        msg = f"Error parsing input:\n{e}\n{err_line}\n{err_marker}"
        raise RuntimeError(msg)

    trans_tree = transformer.transform(parse_tree)

    rendered_tree = template.render(**trans_tree)
    rendered_tree = black.format_str(rendered_tree, mode=black.Mode())
    return rendered_tree
