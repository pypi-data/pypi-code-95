#!/usr/bin/env python
from setuptools import setup


def collect_plugins():
    # TODO: pull this into a generic build-time plugin collection mechanism
    return {
        "localstack.plugins.cli": [
            "pro = localstack_ext.cli.localstack:ProCliPlugin",
        ]
    }


entry_points = dict()
entry_points.update(collect_plugins())

setup(entry_points=entry_points)
