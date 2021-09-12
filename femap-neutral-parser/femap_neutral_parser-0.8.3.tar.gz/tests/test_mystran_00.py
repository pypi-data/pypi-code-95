#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test neutral file generated with MYSTRAN
"""

import os
import tempfile

import numpy as np
import pytest
from click.testing import CliRunner

from femap_neutral_parser import Parser, blocks

from .test_utils import datadir, tempdir  # fixtrures


@pytest.fixture(scope="module")
def neutral(datadir):
    fpath = os.path.join(datadir, "mystran_00.NEU")
    return Parser(fpath)


@pytest.fixture(scope="module")
def f_neutral(datadir):
    fpath = os.path.join(datadir, "FEMAP_v8-2.neu")
    return Parser(fpath)


def test_basics(neutral):
    assert neutral.header["femap_version"] == "8.2"
    assert neutral.header["db_title"] == "323152540, bulk_model.F06"
    assert neutral.femap_version == "8.2"
    assert neutral.db_title == "323152540, bulk_model.F06"
    # test table of content
    assert neutral._toc == {
        100: [[3, 5]],
        450: [[8, 13], [907, 912]],
        451: [[16, 904], [915, 1598]],
    }
    # check available blocks
    assert neutral.available_blocks() == {
        "header": 100,
        "output_sets": 450,
        "_output_vectors": 451,
    }


# =============================================================================
# Block 450 {{1
# =============================================================================
def test_b450_raw_data(neutral):
    """test Block 450 parsing. Since several Blocks 450 are usually found,
    `_get_block_raw_data` yields a file-like objecy containing each of this
    block
    """
    expected = [
        [
            "       1,\n",
            "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test,          \n",
            "0,1,\n",
            "0.,\n",
            "0,\n",
        ],
        [
            "       2,\n",
            "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test,     \n",
            "0,1,\n",
            "0.,\n",
            "0,\n",
        ],
    ]

    # =========================================================================
    # test raw parsing
    # =========================================================================
    b450s = neutral._get_block_raw_data(450, as_file_like=False)
    for i, b450 in enumerate(b450s):
        # b450 = b450.readlines()
        assert b450 == expected[i]
    # =========================================================================
    # also test file-like parsing
    # =========================================================================
    b450s = neutral._get_block_raw_data(450, as_file_like=True)
    for i, b450 in enumerate(b450s):
        b450 = b450.readlines()
        assert b450 == expected[i]


def test_b450_data(neutral):
    """test Block 450 parsing."""
    expected = [
        {
            "ID": 1,
            "anal_type": 1,
            "from_prog": 0,
            "notes": "",
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test",
            "value": 0.0,
        },
        {
            "ID": 2,
            "anal_type": 1,
            "from_prog": 0,
            "notes": "",
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test",
            "value": 0.0,
        },
    ]
    parsed_block = neutral._parse_blocks(450)
    assert parsed_block.data == expected


def test_b450_get(neutral):
    """test Block 450 parsing."""
    expected = {
        1: {
            "anal_type": "Static",
            "from_prog": "Unknown",
            "integer_format": None,
            "notes": "",
            "process_type": None,
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test",
            "value": 0.0,
        },
        2: {
            "anal_type": "Static",
            "from_prog": "Unknown",
            "integer_format": None,
            "notes": "",
            "process_type": None,
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test",
            "value": 0.0,
        },
    }

    assert neutral.output_sets == expected


# =============================================================================
# Block 451 {{1
# =============================================================================


def test_b451_data(neutral):
    """test Block 451 parsing."""
    expected = [
        {
            "ID": 1,
            "anal_type": 1,
            "from_prog": 0,
            "notes": "",
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test",
            "value": 0.0,
        },
        {
            "ID": 2,
            "anal_type": 1,
            "from_prog": 0,
            "notes": "",
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test",
            "value": 0.0,
        },
    ]
    parsed_block = neutral._parse_blocks(451)
    data = parsed_block.data
    assert len(data) == 84
    assert set(data[0].keys()) == {
        "abs_max",
        "calc_warn",
        "cent_total",
        "comp_dir",
        "component_vec",
        "ent_type",
        "id_max",
        "id_min",
        "max_val",
        "min_val",
        "out_type",
        "record",
        "setID",
        "title",
        "vecID",
    }

    assert data[0]["vecID"] == 10001
    assert data[1]["vecID"] == 10002
    # ...
    assert data[-1]["vecID"] == 50212
    # -------------------------------------------------------------------------
    # full check for last vector
    expected = {
        "abs_max": 45.04958,
        "calc_warn": True,
        "cent_total": True,
        "comp_dir": 3,
        "component_vec": [50201.0, 50202.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "ent_type": 8,
        "id_max": 1,
        "id_min": 4,
        "max_val": 45.04958,
        "min_val": -2.221523,
        "out_type": 3,
        "setID": 2,
        "title": "BAR EndB Plane1 Moment",
        "vecID": 50202,
    }
    # we drop the array frm data structure since it requires a specific test
    act_without_array = data[-11].copy()
    actual_records = act_without_array.pop("record")
    assert act_without_array == expected
    expected_records = np.array(
        [
            (1, 4.504958e01),
            (2, 5.241556e-01),
            (3, 1.331676e01),
            (4, -2.221523e00),
            (5, 1.318767e-11),
            (6, -1.419975e-14),
            (9, -2.878763e-01),
            (10, 6.273498e-01),
            (11, 5.241556e-01),
        ],
        dtype=[("entityID", "<i8"), ("value", "<f8")],
    )
    np.testing.assert_array_equal(actual_records, expected_records)


def test_b451_get(neutral, f_neutral):
    """test Block 451 parsing."""
    expected = {
        1: {
            "anal_type": "Static",
            "from_prog": "Unknown",
            "integer_format": None,
            "notes": "",
            "process_type": None,
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test",
            "value": 0.0,
        },
        2: {
            "anal_type": "Static",
            "from_prog": "Unknown",
            "integer_format": None,
            "notes": "",
            "process_type": None,
            "title": "Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test",
            "value": 0.0,
        },
    }
    # -------------------------------------------------------------------------
    # check lazy loading
    assert "_output_vectors" not in dir(neutral)  # NOT loaded
    rss_translation_LCID2 = neutral._output_vectors["disp::t_total"][2].copy()
    assert "_output_vectors" in dir(neutral)  # loaded
    values = rss_translation_LCID2.pop("record")
    assert rss_translation_LCID2 == {
        "abs_max": 2.578386,
        "calc_warn": True,
        "cent_total": True,
        "comp_dir": 1,
        "component_vec": [10002.0, 10003.0, 10004.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "id_max": 7,
        "id_min": 1,
        "max_val": 2.578386,
        "min_val": 0.0,
        "vecID": 10001,
    }
    expected_values = np.array(
        [
            (1, 0.000000e00),
            (2, 2.045391e-01),
            (3, 0.000000e00),
            (4, 1.468270e-02),
            (5, 9.231050e-05),
            (6, 6.276400e-01),
            (7, 2.578386e00),
            (8, 1.025100e-01),
            (9, 2.578363e00),
            (10, 1.916094e00),
            (11, 1.100510e00),
            (12, 2.389742e00),
        ],
        dtype=[("NodeID", "<i8"), ("disp::t_total", "<f8")],
    )
    np.testing.assert_array_equal(values, expected_values)
    # also check initial key
    # rss_translation_LCID2 = neutral._output_vectors["RSS translation"][2].copy()


def test_vectors_agg(neutral, f_neutral):
    expected = np.array(
        [
            (1, 0.0, 0.0, 0.0000000e00, 1),
            (2, -0.1870816, 0.0, 0.0000000e00, 1),
            (3, 0.0, 0.0, 0.0000000e00, 1),
            (4, 0.07011177, 0.0, 0.0000000e00, 1),
            (5, 0.0, 0.0, -5.7721190e-03, 1),
            (6, 0.0, 0.0, -5.6935130e-01, 1),
            (7, 0.0, 0.0, -1.2992963e00, 1),
            (8, -0.0937607, 0.0, -5.7549970e-03, 1),
            (9, 0.03555086, 0.0, -1.2992791e00, 1),
            (10, 0.0, 0.0, -1.5645016e00, 1),
            (11, 0.0, 0.0, -9.5607290e-01, 1),
            (12, 0.0, 0.0, -1.6029116e00, 1),
            (1, 0.0, 0.0, 0.0000000e00, 2),
            (2, -0.2045391, 0.0, 0.0000000e00, 2),
            (3, 0.0, 0.0, 0.0000000e00, 2),
            (4, -0.0146827, 0.0, 0.0000000e00, 2),
            (5, 0.0, 0.0, -9.2310500e-05, 2),
            (6, 0.0, 0.0, -6.2763990e-01, 2),
            (7, 0.0, 0.0, -2.5783863e00, 2),
            (8, -0.1025099, 0.0, -9.2036680e-05, 2),
            (9, -0.00744509, 0.0, -2.5783525e00, 2),
            (10, 0.0, 0.0, -1.9160941e00, 2),
            (11, 0.0, 0.0, -1.1005101e00, 2),
            (12, 0.0, 0.0, -2.3897419e00, 2),
        ],
        dtype=[
            ("NodeID", "<i8"),
            ("disp::t1", "<f8"),
            ("disp::t2", "<f8"),
            ("disp::t3", "<f8"),
            ("SubcaseID", "<i8"),
        ],
    )
    expected = np.rec.array(expected)
    vec = neutral.vectors(
        ("disp::t1", "disp::t2", "disp::t3")
    )
    f_vec = neutral.vectors(
        ("disp::t1", "disp::t2", "disp::t3")
    )
    np.testing.assert_array_almost_equal(f_vec.view(None), expected.view(None))
    np.testing.assert_array_almost_equal(vec.view(None), expected.view(None))


def test_info(neutral):
    info = neutral.info(doprint=False)
    expected = [
        "\nAnalysis",
        "========",
        " * subcase 1: Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc1. test "
        "(MYSTRAN::Static)",
        " * subcase 2: Analyse. NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - lc2. test "
        "(MYSTRAN::Static)",
        "\nOutputs",
        "=======",
        "access to one of them using `._output_vectors[<title>][<SubcaseID>]['record']\n",
        " * disp::t_total -> RSS translation",
        " * disp::t1 -> T1 translation",
        " * disp::t2 -> T2 translation",
        " * disp::t3 -> T3 translation",
        " * disp::r_total -> RSS rotation",
        " * disp::r1 -> R1 rotation",
        " * disp::r2 -> R2 rotation",
        " * disp::r3 -> R3 rotation",
        " * force_applied::f_total -> RSS applied force",
        " * force_applied::f1 -> T1 applied force",
        " * force_applied::f2 -> T2 applied force",
        " * force_applied::f3 -> T3 applied force",
        " * force_applied::m_total -> RSS applied moment",
        " * force_applied::m1 -> R1 applied moment",
        " * force_applied::m2 -> R2 applied moment",
        " * force_applied::m3 -> R3 applied moment",
        " * force_reac::f_total -> RSS SPC force",
        " * force_reac::f1 -> T1 SPC force",
        " * force_reac::f2 -> T2 SPC force",
        " * force_reac::f3 -> T3 SPC force",
        " * force_reac::m_total -> RSS SPC moment",
        " * force_reac::m1 -> R1 SPC moment",
        " * force_reac::m2 -> R2 SPC moment",
        " * force_reac::m3 -> R3 SPC moment",
        " * force_cbar::bending_moment_a1 -> BAR EndA Plane1 Moment",
        " * force_cbar::bending_moment_b1 -> BAR EndB Plane1 Moment",
        " * force_cbar::bending_moment_a2 -> BAR EndA Plane2 Moment",
        " * force_cbar::bending_moment_b2 -> BAR EndB Plane2 Moment",
        " * force_cbar::shear_a1 -> BAR EndA Pl1 Shear Force",
        " * force_cbar::shear_b1 -> BAR EndB Pl1 Shear Force",
        " * force_cbar::shear_a2 -> BAR EndA Pl2 Shear Force",
        " * force_cbar::shear_b2 -> BAR EndB Pl2 Shear Force",
        " * force_cbar::axial_a -> BAR EndA Axial Force",
        " * force_cbar::axial_b -> BAR EndB Axial Force",
        " * force_cbar::torque_a -> BAR EndA Torque",
        " * force_cbar::torque_b -> BAR EndB Torque",
        " * stress_cbar::comb_a1 -> BAR EndA Pt1 Comb Stress",
        " * stress_cbar::comb_b1 -> BAR EndB Pt1 Comb Stress",
        " * stress_cbar::comb_a2 -> BAR EndA Pt2 Comb Stress",
        " * stress_cbar::comb_b2 -> BAR EndB Pt2 Comb Stress",
        " * stress_cbar::comb_a3 -> BAR EndA Pt3 Comb Stress",
        " * stress_cbar::comb_b3 -> BAR EndB Pt3 Comb Stress",
        " * stress_cbar::comb_a4 -> BAR EndA Pt4 Comb Stress",
        " * stress_cbar::comb_b4 -> BAR EndB Pt4 Comb Stress",
        " * stress_cbar::max_comb_a -> BAR EndA Max Stress",
        " * stress_cbar::max_comb_b -> BAR EndB Max Stress",
        " * stress_cbar::min_comb_a -> BAR EndA Min Stress",
        " * stress_cbar::min_comb_b -> BAR EndB Min Stress",
    ]

    assert info == expected


def test_get_local_forces(neutral):
    df = neutral.get_bar_local_forces(asdf=True)
