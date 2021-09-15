#!/usr/bin/env python3

import sys, re

def pytest_ignore_collect(path, config):
    v = sys.version_info
    m = re.search(r'python(\d)(\d)', str(path))

    if m:
        major, minor = map(int, m.groups())
        return major > v.major or minor > v.minor

