"""Autodoc to create automatic documentation
"""
import logging
import shlex
import shutil
import subprocess as sp
from pathlib import Path
import string
import re
import textwrap

import numpy as np
import pandas as pd
import tabulate

from gridsource import Data as IVData
from gridsource.validation import load_yaml

INDENT = "   "
HEADERS = ["=", "-", '"', "'", "~"]


# =============================================================================
# a few RST helpers
# =============================================================================
def _write(txt="", indent=0, header=None, label=True):
    _txt = txt
    if header:
        txt = "\n%s" % txt
        txt += "\n" + len(txt) * HEADERS[header - 1] + "\n"
        if label:
            txt = "\n" + _make_label(_txt) + txt
    # indenting
    txt = textwrap.indent(txt, prefix=INDENT * indent, predicate=lambda line: True)

    return txt + "\n"


def _indent(txt, indent):
    """
    :param txt:
    :param indent:
    :return:
    """
    if indent == 0:
        return txt
    else:
        if isinstance(txt, list):
            txt = "\n".join(txt)
    txt = textwrap.indent(txt, prefix=INDENT * indent, predicate=lambda line: True)
    return txt + "\n"


def _comment(txt):
    # ensure comment has no blank line
    return _directive(content=txt)


def _include(filename, relative_to=False, relative_prefix=None, literal=False):
    if isinstance(filename, str):
        filename = Path(filename)
    if relative_to:
        filename = filename.relative_to(relative_to)
        if relative_prefix:
            filename = relative_prefix / filename
    include = "include"
    if literal:
        include = "literal" + include
    return f"\n.. {include}:: {filename}\n\n"


# =============================================================================
# slugification and label forger
# =============================================================================
ROLES = re.compile(":\w+:")
DUPLICATED = re.compile("(_){2,}")
REMAINS = re.compile("\W")


def _slugify(text):
    text = ROLES.sub("", text)
    text = REMAINS.sub("_", text)
    text = DUPLICATED.sub("_", text)
    return text.strip("_").strip("=").lower()


def _make_label(text, prefix=""):
    text = _slugify(text)
    if prefix:
        return f"\n.. _{prefix}_{text}:\n"
    return f"\n.. _{text}:\n"


def _directive(name="", arg=None, fields=None, content=None, indent=0):
    """
    :param name: the directive itself to use
    :param arg: the argument to pass into the directive
    :param fields: fields to append as children underneath the directive
    :param content: the text to write into this element
    :param indent: (optional default=0) number of characters to indent this element
    :return:

    Add a comment with a not-named directive:

    >>> print(_directive(content='bla\\nbla'))
    .. bla
       blad
    """
    o = list()
    if name:
        o.append(".. {0}::".format(name))
    else:
        o.append("..")

    if arg is not None:
        o[0] += " " + arg

    if fields is not None:
        for k, v in fields:
            o.append(_indent(":" + k + ": " + str(v), indent=1))

    if content is not None:
        if name:
            o.append("")

        if isinstance(content, list):
            o.extend(_indent(content, 1))
        else:
            o.append(_indent(content, 1))
        if not name:
            # merge 1st and second item, since comments must start next to ".."
            old_o = o[:]
            o = [old_o[0] + old_o[1]] + old_o[2:]
    return "\n".join(o)


def _new_public_file(
    filename,
    titles=(),
    includes=(),
    clue_message=True,
):
    """create a file at `filename` path structured as follows:

    titles[0][0], leveled at level titlels[0][1]
    titles[1][0], leveled at level titlels[2][1]
    ...

    Please edit {filename} to provide adequate description.

    includes[0]

    includes[1]

    ...

    """
    if not filename.exists():
        with open(filename, "w") as fh:
            # write titles
            for title, title_level in titles:
                fh.write(_write(title, header=title_level))
            if clue_message:
                fh.write(_write(f"Please edit Me (``{filename}``)"))
            else:
                fh.write(_comment(f"Please edit Me (``{filename}``)"))

            for include_target, relative_to in includes:
                fh.write(_include(include_target, relative_to=relative_to))


class VDataAutodoc:
    """Document a set of columns (aka `tab`)"""

    def __init__(self, ivdata_obj, target_dir=None):
        self.schemas = ivdata_obj._schemas
        if not target_dir:
            target_dir = Path.home()
        if isinstance(target_dir, str):
            target_dir = Path(target_dir)
        self.target_dir = target_dir
        logging.info(f"output in {target_dir}")
        if not self.exists():
            if self.target_dir.exists():
                raise FileExistsError(
                    "target {target_dir} exists and is not a proper Sphynx folder"
                )
            else:
                logging.warning("Sphinx project does not exist. Please run `.create`")
        else:
            self.src_dir = self.target_dir / "source"

    def create(
        self,
        project_name,
        author,
        version,
        lang="en",
        exist_ok=False,
        templatedir=None,
        **kwargs,
    ):
        if self.target_dir.exists():
            if not exist_ok:
                raise FileExistsError(f"target {self.target_dir} exists")
            else:
                shutil.rmtree(self.target_dir)
        # -----------------------------------------------------------------
        # create project structure
        cmd = f"sphinx-quickstart --sep -p {project_name} -a {author} -v {version} -l {lang} {self.target_dir} -q --ext-mathjax"
        if templatedir:
            cmd += f" --templatedir {templatedir} "
        # =====================================================================
        # updating expected mastertoctree with head and tail chapters
        # =====================================================================
        mastertoctree = (
            ["head.rst"] + kwargs.pop("mastertoctree") + ["tail.rst", "glossary.rst"]
        )
        mastertoctree = _indent("\n".join(mastertoctree), 1)
        cmd += f"-d mastertoctree='{mastertoctree}' "
        cmd += " ".join([f"-d {k}={v}" for k, v in kwargs.items()])
        print(40 * "*")
        print(cmd)
        print(40 * "*")
        sp.run(shlex.split(cmd))
        self.src_dir = self.target_dir / "source"
        # ---------------------------------------------------------------------
        # create head and tails files
        for chapter in ("head.rst", "tail.rst"):
            path = self.src_dir / Path(chapter)
            title = chapter.split(".")[0].title() + " Main Title: Change me!"
            _new_public_file(path, titles=((f"{title}", 1),))
            with open(path, "a") as fh:
                fh.write("\nExemple for a link to a :term:`environment`")
        with open(self.src_dir / "head.rst", "a") as fh:
            fh.write(_write("Fields Naming Conventions", header=2))
            p = "Each sheet Columns (or Fields) will be presented as follows:\n\n"
            p += "* :gray:`<SHEET>`-:orange:`<field>`: Mandatory field\n"
            p += "* :gray:`<SHEET>`-:green:`<field>`: Padded field\n"
            p += "* :gray:`<SHEET>`-<field>: Optional field\n"
            p += "\nWhere ``<SHEET>`` is the tab featuring the field, and ``<field>`` is the field name."
            fh.write(_write(p))
        # create glossary
        glossary_file = self.src_dir / "glossary.rst"
        _new_public_file(glossary_file, titles=(("Glossary", 1),))
        with open(glossary_file, "a") as fh:
            # fh.write((
            #     ".. Glossary\n"
            #     "   (cf. https://www.sphinx-doc.org/en/master/usage"
            #     "/restructuredtext/directives.html#glossary\n"))
            fh.write(
                """
.. glossary::
   :sorted:

   root directory
   source directory
      The directory which, including its subdirectories, contains all
      source files for one Sphinx project.

   environment
      A structure where information about all documents under the root is
      saved, and used for cross-referencing.  The environment is pickled
      after the parsing stage, so that successive runs only need to read
      and parse new and changed documents.
      """
            )

    def exists(self):
        if not self.target_dir.exists():
            return False
        # we detect if sphynx project based on:
        conf = self.target_dir / "source" / "conf.py"
        makefile = self.target_dir / "Makefile"
        return conf.exists() and makefile.exists()

    def dump_data(
        self,
        skip_tabs=(),
        drop_columns=(),
        rename_columns=(),
        order_columns=("column",),
        tabs_chapters=((None, "*"),),
    ):

        processed_tabs = set()
        for tab_chapter, tabnames in tabs_chapters:
            slugged = tab_chapter.lower().replace(" ", "_")
            master_file = self.src_dir / f"{slugged}.rst"
            _master_file = self.src_dir / f".{slugged}.inc"
            with open(_master_file, "w") as fh:
                pass
            # ---------------------------------------------------------------------
            # Public master file is called "input_data.rst" and is created only
            # if it doesn't exist
            _new_public_file(
                master_file,
                titles=((tab_chapter, 1),),
                includes=((_master_file, self.src_dir),),
            )
            # =====================================================================
            # processing tabs
            # intended file structure is:
            #  self.src_dir ("source")
            #    + root_tabdir ("source/tabs")
            #          + tabname.rst
            #          + .tabname.rst
            # =====================================================================
            root_tabdir = self.src_dir / "tabs"
            root_fielddir = root_tabdir / "fields"
            root_tabdir.mkdir(exist_ok=True)
            root_fielddir.mkdir(exist_ok=True)
            # -----------------------------------------------------------------
            tab_header_level = 2
            if tabnames == "*":
                # retrieve remaining tabs
                tabnames = set(self.schemas.keys()) - processed_tabs
            to_process_tabs = set(tabnames) - set(skip_tabs)
            for tab_no, tab in enumerate(tabnames):
                processed_tabs.add(tab)
                if tab not in to_process_tabs:
                    continue
                to_process_tabs.discard(tab)
                schema = self.schemas[tab]
                # -----------------------------------------------------------------
                # create public tab description file `source/tabs/<tab>.rst`
                filename = root_tabdir / f"{tab}.inc"
                if not filename.exists():
                    _new_public_file(filename)
                # -----------------------------------------------------------------
                # update private master file
                with open(_master_file, "a") as fh:
                    fh.write(_write(f'Sheet "``{tab}``"', header=tab_header_level))
                    # include public tab description file `source/tabs/<tab>.rst`
                    fh.write(_include(filename, relative_to=self.src_dir))
                    # =================================================================
                    # columns description
                    # =================================================================
                    fh.write(_write(".. glossary::\n\n"))
                    columns = {k: v["items"] for k, v in schema.columns_specs.items()}
                    for colname, colspecs in columns.items():
                        col_status = field_status(colname, schema)
                        # add label
                        if col_status == "padded":
                            _col_status = ":green:`padded`"
                            definition_key = f":green:`{colname}`"
                        elif col_status == "mandatory":
                            _col_status = ":orange:`mandatory`"
                            definition_key = f":orange:`{colname}`"
                        else:
                            _col_status = ""
                            definition_key = f"{colname}"
                        definition_key = f"\n:gray:`{tab.upper()}`-" + definition_key
                        fh.write(_write(definition_key, 1))
                        if "anyOf" in colspecs:
                            anyOf = [d["type"] for d in colspecs.pop("anyOf")]
                            colspecs["type"] = ", ".join(anyOf)
                        if "default" in colspecs and colspecs["default"] == "":
                            colspecs["default"] = '""'
                        # if colname == "repeat_discard_nth":
                        #     breakpoint()
                        avoid = ("example",)
                        colspecs = {k: v for k, v in colspecs.items() if k not in avoid}
                        definition = (
                            " | ".join([f"{k}: ``{v}``" for k, v in colspecs.items()])
                            + "\n"
                        )
                        colspecs["status"] = _col_status
                        field_public_file = root_fielddir / f"{tab}::{colname}.inc"
                        _new_public_file(field_public_file, clue_message=False)
                        definition_include = _include(
                            field_public_file,
                            relative_to=self.src_dir,
                        )
                        fh.write(_write(definition + definition_include, indent=2))
                        columns[colname] = colspecs.copy()
                    # ---------------------------------------------------------
                    # columns description summary
                    df = pd.DataFrame.from_dict(columns, orient="index")
                    df.index.names = ["column"]
                    if "type" in df.columns:
                        df["type"] = df["type"].replace(
                            {
                                "number": "``float``",
                                "integer": "``int``",
                                "string": "``str``",
                            }
                        )
                    # -------------------------------------------------------------
                    # process special columns
                    _uniq = dict(schema.uniqueness_sets)
                    if _uniq:
                        _uniq = {f"Set ({id})": v for id, v in _uniq.items()}
                        uniq = {}
                        for id, cols in _uniq.items():
                            for col in cols:
                                uniq[col] = id
                        df["set"] = pd.Series(uniq)
                        df["set"] = df.set.fillna("")
                    # -------------------------------------------------------------
                    # bold index
                    df.reset_index(inplace=True)
                    df["column"] = "**" + df["column"].astype(str) + "**"
                    # -------------------------------------------------------------
                    # order columns
                    cols = list(order_columns)
                    cols += [c for c in df if c not in cols]  # append remaining columns
                    cols = [
                        c for c in cols if c in df
                    ]  # ensure all columns are exiting
                    df = df[cols]
                    # -------------------------------------------------------------
                    # drop columns
                    _drop_columns = [c for c in drop_columns if c in df]
                    if _drop_columns:
                        df = df.drop(columns=_drop_columns)
                    # -------------------------------------------------------------
                    # rename columns
                    _rename_columns = {
                        prev: new for prev, new in rename_columns.items() if prev in df
                    }
                    if _rename_columns:
                        df = df.rename(columns=_rename_columns)
                    # -------------------------------------------------------------
                    # clean and order
                    df = df.fillna("")
                    table = tabulate.tabulate(
                        df, headers="keys", tablefmt="rst", showindex=False
                    )
                    # ---------------------------------------------------------
                    # table caption
                    fh.write(_write(f"\n.. table:: {tab} columns specifications\n"))
                    fh.write(_write(table, indent=1))
                    fh.write("\n")
                    # ---------------------------------------------------------
                    # note about uniqueness sets
                    if _uniq:
                        msg = "The following set(s) of columns combination need to be unique:\n\n"
                        for uniq, cols in _uniq.items():
                            columns = ", ".join([f"``{c}``" for c in cols])
                            msg += f"  * ``{uniq}``: {columns}\n"
                        fh.write(_directive(name="note", content=msg))
                    # ---------------------------------------------------------
                    # xref
                    if schema.xcalling:
                        df = pd.DataFrame(
                            schema.xcalling, index=["Xref sheet", "Xref column"]
                        ).T
                        df.index.names = ["column"]
                        df.reset_index(inplace=True)
                        table = tabulate.tabulate(
                            df, headers="keys", tablefmt="rst", showindex=False
                        )
                        msg = "The following column(s) need to refer to existing value(s) from other sheet(s):\n\n"
                        msg += _write(f"\n.. table:: {tab} columns cross-references\n")
                        msg += _write(table, indent=1)

                        fh.write(_directive(name="note", content=msg))
                    if len(to_process_tabs) > 0:
                        fh.write(_write("\n-------------------------\n"))


# =============================================================================
# dumping XLSX template
# =============================================================================
FMTS = {
    "default": {
        "bold": True,
        "font_color": "#3A81CC",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "bg_color": "#eeeeec",
    },
    "mandatory": {"bg_color": "#fcaf3e", "color": "black"},
    "padded": {"bg_color": "#8ae234", "color": "black"},
    "units": {"bg_color": "#729fcf", "color": "black"},
}


def fmt_dict(attributes=()):
    fmt = FMTS["default"].copy()
    for attr in attributes:
        _d = FMTS[attr].copy()
        fmt.update(_d)
    return fmt


def dump_xlsx_template(schemas, output, tabs=(), excluded_tabs=None):
    """creates a blank XSLX spreadsheet based on provided schema"""
    # -------------------------------------------------------------------------
    # read shema(s)
    data = IVData()
    data.read_schema(*schemas)
    # -------------------------------------------------------------------------
    # eventually filter with tabs wishlist
    schemas = data._schemas.copy()
    if tabs:
        schemas = {k: v for k, v in schemas.items() if k in tabs}
    if excluded_tabs:
        schemas = {k: v for k, v in schemas.items() if k not in excluded_tabs}
    # -------------------------------------------------------------------------
    # check implicit tabs xcalls
    tabs = list(tabs)
    for tabname, schema in schemas.items():
        for referencing_col, (
            referenced_tab,
            referenced_col,
        ) in schema.xcalling.items():
            if referenced_tab not in tabs:
                logging.warning(f"add referenced {referenced_tab}")
                tabs.append(referenced_tab)
    data._schemas = schemas
    cols = data.dump_template()  # get columns and attributes
    cols = {k: cols[k] for k in tabs}  # reorder as required by `tabs` order
    with pd.ExcelWriter(output) as writer:
        workbook = writer.book
        # prepare formats
        default_format = workbook.add_format(fmt_dict())
        mandatory_format = workbook.add_format(fmt_dict(["mandatory"]))
        padded_format = workbook.add_format(fmt_dict(["padded"]))
        units_format = workbook.add_format(fmt_dict(["units"]))
        for tabname, data in cols.items():
            df = data["df"]
            colspecs = data["schema"]
            required = data["required"]
            xcallings = data["xcalling"]
            df.to_excel(
                writer, sheet_name=tabname, startrow=1, header=False, index=False
            )
            worksheet = workbook.sheetnames[tabname]
            # -----------------------------------------------------------------
            # format header
            # worksheet.set_row(0, height=None, cell_format=mandatory_format)
            ws_has_units = {cs.get("units") for _, cs in colspecs.items()} > {None}
            for i, colname in enumerate(df.columns):
                colname_status = field_status(colname, schemas[tabname])
                if colname_status == "default":
                    fmt = default_format
                elif colname_status == "padded":
                    fmt = padded_format
                elif colname_status == "mandatory":
                    fmt = mandatory_format
                else:
                    raise ValueError(f"dont know anythin about {colname_status=}")
                # is_mandatory = colname in required
                pattern = colspecs[colname]["items"].get("pattern")
                default = colspecs[colname]["items"].get("default")
                xcalling = xcallings.get(colname)
                worksheet.write_string(0, i, colname, cell_format=fmt)
                cell_header = "{col}{row}".format(col=string.ascii_uppercase[i], row=1)
                # -------------------------------------------------------------
                # process comments
                types = set((colspecs[colname]["items"].get("type"),))
                for typ in colspecs[colname]["items"].get("anyOf", []):
                    types.add(typ["type"])
                types.discard(None)
                types_str = ", ".join(types)
                comment = f"Type(s): {types_str}"
                if colspecs[colname]["uniqueItems"]:
                    comment += f"\nMust be Unique"
                if pattern:
                    comment += f"\nPattern: {pattern}"
                if xcalling:
                    comment += f"\ncross-ref: {xcalling[0]}/{xcalling[1]}"
                if default is not None:
                    if isinstance(default, str):
                        comment += f'\ndefault: "{default}"'
                    else:
                        comment += f"\ndefault: {default}"
                worksheet.write_comment(
                    cell_header,
                    comment,
                    {
                        "author": "numeric-GmbH",
                        "color": "#ad7fa8",
                        "visible": False,
                    },
                )
            if ws_has_units:
                worksheet.set_row(1, height=None, cell_format=units_format)
                worksheet.freeze_panes(2, 1)
            else:
                worksheet.freeze_panes(1, 1)
            # -----------------------------------------------------------------
            # autofit
    logging.info(f"finilized {output}")
    return output


def field_status(colname, schema):
    """return one of {'mandatory', 'padded', 'default'"""
    is_mandatory = colname in schema.required
    pattern = schema.columns_specs[colname]["items"].get("pattern")
    if pattern and not re.match(pattern, ""):
        is_mandatory = True
    default = schema.columns_specs[colname]["items"].get("default")
    is_padded = False
    if default == "_pad_":
        is_mandatory = False
        is_padded = True
    # xcalling = schema.xcalling.get(colname)
    if is_mandatory:  # or xcalling:
        status = "mandatory"
    elif is_padded:
        status = "padded"
    else:
        status = "default"
    return status


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
