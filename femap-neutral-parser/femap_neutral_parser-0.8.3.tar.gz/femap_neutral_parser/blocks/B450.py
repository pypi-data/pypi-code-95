"""
This module contains defined blocks. Any block shall inherit from `Block`.
"""

import logging

from femap_neutral_parser.blocks._base import Block

FROM_PROG = {
    0: "Unknown",
    1: "FEMAP Generated",
    2: "PAL",
    3: "PAL 2",
    4: "MSC/NASTRAN",
    5: "ANSYS",
    6: "STARDYNE",
    7: "COSMOS",
    8: "PATRAN",
    9: "FEMAP Neutral",
    10: "ALGOR",
    11: "SSS/NASTRAN",
    12: "Comma Separated",
    13: "UAI/NASTRAN",
    14: "Cosmic NASTRAN",
    15: "STAAD",
    16: "ABAQUS",
    17: "WECAN",
    18: "MTAB/SAP",
    19: "CDA/Sprint",
    20: "CAEFEM",
    21: "I-DEAS",
    22: "ME/NASTRAN",
    26: "CSA/NASTRAN",
    27: "CFDesign",
    28: "LS-DYNA",
    29: "MARC",
    30: "SINDA",
    31: "NE/Nastran",
    32: "SAToolkit",
    33: "TMG",
    34: "FEMAP Structural",
    35: "VR/Nastran",
    36: "NX Nastran",
}

ANAL_TYPE = {
    0: "Unknown",
    1: "Static",
    2: "Modes",
    3: "Transient",
    4: "Frequency Response",
    5: "Response Spectrum",
    6: "Random",
    7: "Linear Buckling",
    8: "Design Opt",
    9: "Explicit",
    10: "Nonlinear Static",
    11: "Nonlinear Buckling",
    12: "Nonlinear Transient",
    19: "Comp Fluid Dynamics",
    20: "Steady State Heat Transfer",
    21: "Transient Heat",
    22: "Advanced Nonlinear Static",
    23: "Advanced Nonlinear Transient",
    24: "Advanced Nonlinear Explicit",
    25: "Static Aeroelasticity",
    26: "Aerodynamic Flutter",
    27: "Multistep Nonlinear",
    28: "Multistep_Kinematic",
    29: "Preload",
}

PROCESS_TYPE = {
    0: "None",
    1: "Linear Combination",
    2: "RSS Combination",
    3: "Max Envelope",
    4: "Min Envelope",
    5: "AbsMax Envelope",
    6: "Max Envelope SetID",
    7: "Min Envelope SetID",
    8: "AbsMax Envelope SetID",
}


class B450(Block):
    """
    >>> txt = '''           1,
    ... Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test,
    ... 0,1
    ... 0.,
    ... 2,
    ... This is a line
    ... and a second one
    ... 1, 2
    ... '''
    >>> b = B450(version=11.1)
    >>> from pprint import pprint as pp
    >>> b.parse(txt)
    >>> b.data == [{
    ...  'ID': 1,
    ...  'anal_type': 1,
    ...  'attach_id': 1,
    ...  'from_prog': 0,
    ...  'location_id': 2,
    ...  'notes': 'This is a line\\nand a second one',
    ...  'title': 'Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test',
    ...  'value': 0.0}]
    True
    >>> b.digest() == {
    ... 1: {'anal_type': 'Static',
    ...          'from_prog': 'Unknown',
    ...          'integer_format': None,
    ...          'notes': 'This is a line\\nand a second one',
    ...          'process_type': None,
    ...          'title': 'Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test',
    ...          'value': 0.0}}
    True
    """

    NAME = "output_sets"
    RECORDS = [
        [
            {"field": "ID", "coerce": int},
        ],  # 1
        [
            {"field": "title"},
        ],  # 2
        [
            {"field": "from_prog", "coerce": int},  # 3
            {"field": "anal_type", "coerce": int},
            {"field": "process_type", "coerce": int, "v+": "11.2"},
            {"field": "integer_format", "coerce": bool, "v+": "11.2"},
        ],
        [
            {"field": "value", "coerce": float},
        ],  # 4
        [
            {"field": "nlines", "coerce": int, "is_offset": True},
        ],  # 5
        [
            {"field": "notes"},
        ],  # may be null
        [
            {"field": "attach_id", "coerce": int, "v+": "11.0"},  # 6
            {"field": "location_id", "coerce": int, "v+": "11.0"},
            {"field": "study_id", "coerce": int, "v+": "11.2"},
        ],
    ]

    def digest(self):

        ret = {}
        for dic in self.data:
            ret[dic["ID"]] = {
                "title": dic["title"],
                "from_prog": FROM_PROG[dic["from_prog"]],
                "anal_type": ANAL_TYPE[dic["anal_type"]],
                "process_type": PROCESS_TYPE.get(dic.get("process_type")),
                "integer_format": dic.get("integer_format"),
                "value": dic["value"],
                "notes": dic["notes"],
            }
            not_parsed = set(("attach_id", "study_id", "location_id")) & set(dic.keys())
            if not_parsed:
                logging.warning(f"data named {not_parsed} not implemented for now!")
        return ret


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
