"""
This module contains defined blocks. Any block shall inherit from `Block`.
"""

import logging
from collections import defaultdict

from femap_neutral_parser.blocks._base import Block
from femap_neutral_parser.utils import CaseInsensitiveDict

# =============================================================================
# Block B451
# =============================================================================


class B451(Block):
    """
    >>> txt = '''       1,   10001,       1
    ... RSS translation
    ...      0.000000E+00,     1.602912E+00,     1.602912E+00,
    ...    10002,   10003,   10004,       0,       0,       0,       0,       0,       0,       0,
    ...        0,       0,       0,       0,       0,       0,       0,       0,       0,       0,
    ...        1,      12,       1,       7,
    ...        1,       1,       1
    ...        1,     0.000000E+00,
    ...        2,     1.870816E-01,
    ...        3,     0.000000E+00,
    ...        4,     7.011176E-02,
    ...       -1,     0.          ,
    ... '''
    >>> b = B451(version=9.3)
    >>> b.parse(txt)
    >>> __import__('pprint').pprint(b.data)
    [{'abs_max': 1.602912,
      'calc_warn': True,
      'cent_total': True,
      'comp_dir': 1,
      'component_vec': [10002.0,
                        10003.0,
                        10004.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0],
      'ent_type': 7,
      'id_max': 12,
      'id_min': 1,
      'max_val': 1.602912,
      'min_val': 0.0,
      'out_type': 1,
      'record': array([(1, 0.        ), (2, 0.1870816 ), (3, 0.        ), (4, 0.07011176)],
          dtype=[('entityID', '<i8'), ('value', '<f8')]),
      'setID': 1,
      'title': 'RSS translation',
      'vecID': 10001}]
    """

    NAME = "_output_vectors"
    RECORDS = [
        [
            {"field": "setID", "coerce": int},
            {"field": "vecID", "coerce": int},
            {"field": "_", "coerce": int},
        ],  # 1
        [
            {"field": "title"},
        ],  # 2
        [
            {"field": "min_val", "coerce": float},  # 3
            {"field": "max_val", "coerce": float},
            {"field": "abs_max", "coerce": float},
        ],
        [  # 4 comp[0..9]
            {"field": "component_vec", "coerce": float, "single_line_array": 10},
        ],
        [  # 5 comp[10..19]
            {"field": "_", "coerce": float, "single_line_array": 10},
        ],
        [  # 6
            {"field": "doubled_sided_contour", "coerce": int, "v+": "10.0"},
        ],
        [  # 7
            {"field": "id_min", "coerce": int},
            {"field": "id_max", "coerce": int},
            {"field": "out_type", "coerce": int},
            {"field": "ent_type", "coerce": int},
        ],
        [  # 8
            {"field": "calc_warn", "coerce": bool},
            {"field": "comp_dir", "coerce": int, "v+": "4.1"},
            {"field": "cent_total", "coerce": bool},
        ],
        [  # 1 record for each entry, plus last record
            {
                "multi_line_array": True,
                "field": "record",
                "fields": ("entityID", "value"),
                "coerce": (int, float),
            },
        ],
    ]

    def digest(self, translate):
        agg = defaultdict(dict)  # returned dictionnary
        for data in self.data:
            # -----------------------------------------------------------------
            # affect appropriate columns headers
            ent_type = {7: "NodeID", 8: "ElementID"}[data.pop("ent_type")]
            out_type = {
                0: "value",
                1: "disp",
                2: "accel",
                3: "force",
                4: "stress",
                5: "strain",
                6: "temp",
            }.get(data.pop("out_type"), "user")
            # -----------------------------------------------------------------
            # modify MYSTRAN titles removing duplicated blanks
            title = " ".join(data.pop("title").split())
            vector, new_title = translate(key=title)
            new_title = "::".join((vector, new_title))
            set_id = data.pop("setID")
            data["record"].dtype.names = (ent_type, new_title)
            agg[new_title][set_id] = data
            # agg[title][set_id] = data  # also store initial keys
        return CaseInsensitiveDict(agg)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    # import sys
    # filepath =sys.argv[1]
