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
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple

import yaml
from pkg_resources import resource_string

from c_sar_denarius import cli
from c_sar_denarius import utils as csd_utils
from c_sar_denarius.md_utils import file_to_md_table
from c_sar_denarius.md_utils import mkdocs
from c_sar_denarius.md_utils import mkdocs_base
from c_sar_denarius.md_utils import title_and_ver

COMP_TYPES = ("control_vs_plasmid", "treatment_vs_plasmid", "treatment_vs_control")


def structure_yaml(version: str, config_ver: str, yamlfile: str):
    logging.info(f"c-sar version for structure was '{version}'")
    if version == "?":
        logging.info(f"Version detected is invalid, using latest known config '{config_ver}'")
        version = config_ver
    yaml_obj = None
    if yamlfile is None:
        # load the raw string
        md_template = resource_string(__name__, f"resources/structure/{version}.yaml").decode("utf-8", "strict")
        yaml_obj = yaml.safe_load(md_template)
    else:
        with open(yamlfile, "r") as yaml_stream:
            yaml_obj = yaml.safe_load(yaml_stream)
    return yaml_obj


def file_to_md(
    input: str,
    output: str,
    subdir: str,
    title: str,
    item: str,
    image=False,
    table=False,
    required=False,
    label=None,
    download=False,
    wildcard=False,
    description=None,
) -> Tuple[str, List[str]]:
    items = []
    full_md = None
    if label is None:
        label = item

    # sample wildcard is only on file name, not folder
    if wildcard:
        pattern = re.compile(item.replace("%S%", "(.+)"))
        for f in os.listdir(os.path.join(input, subdir)):
            m = pattern.fullmatch(f)
            if m is None:
                continue
            (item, sample) = m.group(0, 1)
            if sample == "LFC":
                continue
            items.append({"label": f"{label} - {sample}", "item": item})
    else:
        items.append({"label": label, "item": item})

    for i_dict in items:
        item = i_dict["item"]
        label = i_dict["label"]
        source = os.path.join(input, subdir, item)
        if not os.path.isfile(source):
            if required:
                logging.critical(f"Failed to find file tagged as required: {source}")
                sys.exit(2)
            continue

        if full_md is None:
            full_md = ""

        if table or download or image:
            full_md += f"### {label}\n\n"
            if description:
                full_md += f"{description}\n\n"

        if table:
            full_md += file_to_md_table(source)

        relative = os.path.join("files", subdir, item)
        destination = os.path.join(output, title, relative)
        # all files listed in yaml are copied to files to enable archive building
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copyfile(source, destination)
        if not download and not image:
            # no rendering for these
            continue

        if download:
            full_md += f"[Download](./{relative})\n\n"
        if image:
            full_md += f"![{item}](./{relative})\n\n"
    return full_md


def build_md(input: str, title: str, target: str, version: str, config_ver: str, structure: Dict):
    """
    As we have "unknown" plasmid_vs_control etc we need to build this by iterating over things

    Remember this code 'looks for' things based on the config, it won't tell you about things it's skipping.
    """
    files_seen = []
    comparison_sets = {}
    output = os.path.join(target, "md", "docs")
    seen_comp_label = {}

    for label in structure:
        for p_subdir in structure[label]:
            # what can we find
            for comparison_type in COMP_TYPES:
                comp_label = f"{comparison_type} - {label}"
                subdir = p_subdir.replace("%A%_vs_%B%", comparison_type)
                for p_item in structure[label][p_subdir]:
                    item = p_item.replace("%A%_vs_%B%", comparison_type)
                    data_fn = os.path.join(input, subdir, item)
                    data_file = Path(data_fn)
                    if not data_file.is_file():
                        continue
                    files_seen.append(data_fn)
                    md_element = file_to_md(input, output, subdir, title, item, **structure[label][p_subdir][p_item])
                    if md_element:
                        if comparison_type not in comparison_sets:
                            comparison_sets[comparison_type] = title_and_ver(comparison_type, version, config_ver)

                        if comp_label not in seen_comp_label:
                            comparison_sets[comparison_type] += f"\n\n----\n\n## {label}"
                            seen_comp_label[comp_label] = None

                        comparison_sets[comparison_type] += f"\n\n{md_element}"

    dest = os.path.join(output, title)
    for comparison_type in comparison_sets:
        # write the full MD files
        md_file = os.path.join(dest, comparison_type + ".md")
        with open(md_file, "w") as ofh:
            print(comparison_sets[comparison_type], file=ofh)

    # need to unique this list due to looping over comparison types
    return list(set(files_seen))


def run(input: str, name: str, primary_color: str, yamlfile: str, target: str, loglevel: str):
    cli.log_setup(loglevel)
    (version, config_ver) = csd_utils.c_sar_version(input)
    structure = structure_yaml(version, config_ver, yamlfile)
    md_base = mkdocs_base(target, primary_color)
    final_build = os.path.join(target, "site")
    files_seen = build_md(input, name, target, version, config_ver, structure)
    csd_utils.files_not_seen(input, files_seen)
    mkdocs(md_base, final_build)
