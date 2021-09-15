#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from km3net_testdata import data_path, latest, LATEST_VERSIONS


class TestDataPath(unittest.TestCase):
    def test_access(self):
        assert data_path("online/km3net_online.root").endswith(
            "km3net_online.root")

    def test_accessing_nonexistent_files(self):
        with self.assertRaises(RuntimeError):
            data_path("nonexistent_file")

    def test_filename_returned_if_raise_missing_is_false(self):
        filename = "nonexistent_file"
        assert data_path(filename, raise_missing=False).endswith(filename)


class TestLatest(unittest.TestCase):
    def test_latest_paths(self):
        for dataformat in LATEST_VERSIONS.keys():
            assert latest(dataformat).endswith(LATEST_VERSIONS[dataformat])
