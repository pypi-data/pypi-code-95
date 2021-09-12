#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Carlos Ramos.

import unittest

loader = unittest.TestLoader()
start_dir = './'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)