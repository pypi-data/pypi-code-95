"""
Implementation of the reader for XYZ files using OpenBabel
"""

import os
import seamm
from read_structure_step.errors import MopError
from read_structure_step.formats.registries import register_reader
from ..which import which
from .find_mopac import find_mopac
import re


def _find_charge(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return text.group(2)


def _find_standard(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return text.group(0)


def _find_field(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return (text.group(1), text.group(4), text.group(7))


def _find_open(regex, input_file):
    text = re.search(regex, input_file)
    if text is not None:
        return (text.group(2), text.group(3))


extras = {
    "structure": {
        "net_charge": {
            "regex": r"(CHARGE=)([\+\-]?\d)",
            "find": _find_charge,
            "value": None,
        },
        "field": {
            "regex": (
                r"FIELD=\(([-+]?\d+(\.\d+(e[-+]\d+)?)?)\,([-+]?\d+"
                r"(\.\d+(e[-+]\d+)?)?)\,([-+]?\d+(\.\d+(e[-+]\d+)?"
                r")?)\)"
            ),
            "find": _find_field,
            "value": None,
        },
        "open": {
            "regex": r"(OPEN\()(\d+)\,\s*(\d+)\)",
            "find": _find_open,
            "value": None,
        },
    },
}

obabel_error_identifiers = ["0 molecules converted"]


@register_reader(".mop")
def load_mop(file_name, configuration, **kwargs):

    with open(file_name, "r") as f:
        input_file = f.read()
        for k, v in extras.items():
            for ko, vo in v.items():
                regex = extras[k][ko]["regex"]
                extras[k][ko]["value"] = vo["find"](regex, input_file)

    try:
        obabel_exe = which("obabel")
        local = seamm.ExecLocal()

        result = local.run(
            cmd=[obabel_exe, "-f 1", "-l 1", "-imop", file_name, "-omol", "-x3"]
        )
        for each_error in obabel_error_identifiers:
            if each_error in result["stderr"]:
                raise MopError("OpenBabel: Could not read input file. %s" % result)

        mol = result["stdout"]

        # need to handle extras! extras["structure"]
        configuration.from_molfile_text(mol)
        return

    except MopError:

        mopac_exe = find_mopac()

        if mopac_exe is None:
            raise FileNotFoundError("The MOPAC executable could not be found")

        with open(file_name, "r") as f:
            data = f.read()

            hamiltonians = [
                "AM1",
                "MNDO",
                "MNDOD",
                "PM3",
                "PM6",
                "PM6-D3",
                "PM6-DH+",
                "PM6-DH2",
                "PM6-DH2X",
                "PM6-D3H4",
                "PM6-D3H4X",
                "PM7",
                "PM7-TS",
                "RM1",
            ]

            for hamiltonian in hamiltonians:
                if hamiltonian in data:
                    data = data.replace(hamiltonian, "0SCF", 1)
                    break

        tmp_file = os.path.dirname(file_name) + "/_0SCFTemp.mop"

        with open(tmp_file, "w") as f:
            f.write(data)

        local = seamm.ExecLocal()
        local.run(cmd=[mopac_exe, tmp_file])

        output_file = os.path.dirname(file_name) + "/_0SCFTemp.out"

        obabel_exe = which("obabel")
        local = seamm.ExecLocal()

        result = local.run(
            cmd=[obabel_exe, "-f 1", "-l 1", "-imoo", output_file, "-omol", "-x3"]
        )

        os.remove(tmp_file)
        os.remove(output_file)

        for each_error in obabel_error_identifiers:
            if each_error in result["stderr"]:
                raise MopError("OpenBabel: Could not read input file. %s" % result)

        mol = result["stdout"]

        # need to handle extras! extras["structure"]
        configuration.from_molfile_text(mol)
