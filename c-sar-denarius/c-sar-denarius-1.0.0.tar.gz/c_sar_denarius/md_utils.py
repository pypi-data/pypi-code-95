#
# Copyright (c) 2021 Genome Research Ltd
#
# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>
#
# This file is part of c-sar-denarius.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# 1. The usage of a range of years within a copyright statement contained within
# this distribution should be interpreted as being equivalent to a list of years
# including the first and last year specified and all consecutive years between
# them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
# 2009, 2011-2012’ should be interpreted as being identical to a statement that
# reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
# statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
# identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
# 2009, 2010, 2011, 2012’.
import csv
import logging
import os
import shutil
import subprocess
import tempfile
from typing import List

from pkg_resources import resource_filename
from pkg_resources import resource_string

import c_sar_denarius.utils as csd_utils

MKDOCS_BUILD = "cd %(md_base)s && mkdocs build -d %(tmp_target)s && rsync -ar %(tmp_target)s/* %(target)s"


def mkdocs_base(target, primary_color: "blue-grey"):
    logging.info(f"Building site into: {target}")
    md_base = os.path.join(target, "md")
    # lazily creating structure
    os.makedirs(os.path.join(md_base, "docs", "stylesheets"), exist_ok=True)

    mkdocs_yml = resource_string(__name__, f"resources/templates/mkdocs.yml.tmpl").decode("utf-8", "strict")
    mkdocs_yml = mkdocs_yml.replace("%primary-colour%", primary_color.replace("-", " "))
    with open(os.path.join(md_base, "mkdocs.yml"), "wt") as mdy:
        print(mkdocs_yml, file=mdy)

    index_md = resource_filename(__name__, "resources/templates/index.md.tmpl")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "index.md"))
    index_md = resource_filename(__name__, "resources/other/denarius.png")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "denarius.png"))
    index_md = resource_filename(__name__, "resources/other/denarius.css")
    shutil.copyfile(index_md, os.path.join(md_base, "docs", "stylesheets", "denarius.css"))
    return md_base


def file_to_md_table(f_path: str):
    qc_table = ""
    with open(f_path, "r", newline="\n") as csvfh:
        header = True
        for row in csv.reader(csvfh, delimiter="\t"):
            qc_table += "| " + " | ".join(row) + " |\n"
            if header:
                qc_table += "| " + " | ".join(["---"] * len(row)) + " |\n"
                header = False
    qc_table += "\n"
    return qc_table


def title_and_ver(title, c_sar_version, config_ver):
    md_str = f"# {title}\n\n"
    md_str = f"## Versions\n\n"
    md_str += f"* {c_sar_version} : c-sar\n"
    md_str += f"* {csd_utils.version()} : c-sar-denarius\n"
    md_str += f"* {config_ver} : c-sar-denarius config\n"
    # no trailing new lines
    return md_str


def mkdocs(md_base, final_build):
    """
    sync the docs into the final tree
    generate the site
    move old content of root out of place
    move new content of root into place
    """
    with tempfile.TemporaryDirectory(prefix=__name__) as tmpdir:
        os.makedirs(final_build, exist_ok=True)
        full_command = MKDOCS_BUILD % {
            "md_base": md_base,
            "tmp_target": tmpdir,
            "target": final_build,
        }
        logging.info(f"Generating markdown site, executing: {full_command}")
        r = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            csd_utils.process_log_and_exit(r, "Problem while building mkdocs site")
