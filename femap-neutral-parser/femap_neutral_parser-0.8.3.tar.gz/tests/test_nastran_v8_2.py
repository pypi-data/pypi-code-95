#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test neutral file generated with NX NASTRAN
"""

import os
import tempfile

import pytest
from click.testing import CliRunner

from femap_neutral_parser import Parser, blocks

from .test_utils import datadir, tempdir  # fixtrures


@pytest.fixture(scope="module")
def neutral(datadir):
    fpath = os.path.join(datadir, "FEMAP_v8-2.neu")
    return Parser(fpath)


def test_basics(neutral):
    assert neutral.femap_version[:6] == "8.1999"
    assert neutral.db_title == ""
    # test table of content
    assert neutral._toc == {100: [[2, 4]], 450: [[7, 29]], 451: [[32, 3550]]}


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
            "1,\n",
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC1\n",
            "36,1,\n",
            "0.,\n",
            "6,\n",
            "From: Z:\\13-Projects\\10-Air France\\Seat track "
            "analysis\\7-Floortool\\test\\TC_03-000.op2\n",
            "Date : Mon Apr  5 09:56:49 2021\n",
            "<NULL>\n",
            "ANALYSE\n",
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC1\n",
            "TEST\n",
            "2,\n",
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC2\n",
            "36,1,\n",
            "0.,\n",
            "6,\n",
            "From: Z:\\13-Projects\\10-Air France\\Seat track "
            "analysis\\7-Floortool\\test\\TC_03-000.op2\n",
            "Date : Mon Apr  5 09:56:49 2021\n",
            "<NULL>\n",
            "ANALYSE\n",
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC2\n",
            "TEST\n",
        ]
    ]

    # =========================================================================
    # test raw parsing
    # =========================================================================
    b450s = neutral._get_block_raw_data(450, as_file_like=False)
    b450s = list(b450s)
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
    """test Block 450 parsing.     """
    expected = [
        {
            "ID": 1,
            "anal_type": 1,
            "from_prog": 36,
            "notes": "From: Z:\\13-Projects\\10-Air France\\Seat track "
            "analysis\\7-Floortool\\test\\TC_03-000.op2\n"
            "Date : Mon Apr  5 09:56:49 2021\n"
            "\n"
            "ANALYSE\n"
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC1\n"
            "TEST",
            "title": "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC1",
            "value": 0.0,
        },
        {
            "ID": 2,
            "anal_type": 1,
            "from_prog": 36,
            "notes": "From: Z:\\13-Projects\\10-Air France\\Seat track "
            "analysis\\7-Floortool\\test\\TC_03-000.op2\n"
            "Date : Mon Apr  5 09:56:49 2021\n"
            "\n"
            "ANALYSE\n"
            "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC2\n"
            "TEST",
            "title": "NASTRAN SPC 1 - NASTRAN SPC 1 - NASTRAN SPC 1 - LC2",
            "value": 0.0,
        },
    ]

    parsed_block = neutral._parse_blocks(450)
    assert parsed_block.data == expected
