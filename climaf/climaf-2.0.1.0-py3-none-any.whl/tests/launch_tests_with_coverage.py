#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, unicode_literals, absolute_import


import coverage
import argparse
import os
import sys
import shutil
import multiprocessing
from functools import partial
from contextlib import contextmanager


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def launch_several_processes(func, list_values, max_procs=1, fixed_options=dict()):
    with poolcontext(max_procs) as pool:
        results = pool.map(partial(func, **fixed_options), list_values, chunksize=1)
    return results


def run_coverage(script, cov, run_option):
    cov.set_option("run:parallel", True)
    cov.set_option("run:source", run_option.format(script))
    cov.start()
    import importlib
    my_module = importlib.import_module(script)
    my_module.remove_dir_and_content(my_module.tmp_directory)
    if not os.path.isdir(my_module.tmp_directory):
        os.makedirs(my_module.tmp_directory)
    my_module.setNewUniqueCache(my_module.tmp_directory)
    os.chdir(my_module.tmp_directory)
    my_module.unittest.main()
    my_module.remove_dir_and_content(my_module.tmp_directory)
    cov.stop()
    cov.save()


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--report_ensemble", default=True, type=bool)
parser.add_argument("-m", "--run_modules", action="append")
args = parser.parse_args()


# Path of tests dir
test_dir = os.path.abspath(os.path.dirname(__file__))
html_report_dir = os.sep.join([test_dir, "htmlcov"])

# Add CliMAF path to environment
sys.path.append(os.sep.join([test_dir, ".."]))

# Initialize coverage
cov = coverage.Coverage()

# Remove old results
cov.erase()
if os.path.isdir(html_report_dir):
    shutil.rmtree(html_report_dir)
climaf_macro_file = os.sep.join([test_dir, ".climaf.macros_tests"])
if os.path.exists(climaf_macro_file):
    os.remove(climaf_macro_file)
os.environ["CLIMAF_MACROS"] = climaf_macro_file
cov.set_option("run:parallel", True)

# Run coverage
if args.report_ensemble:
    launch_several_processes(run_coverage, list_values=args.run_modules, max_procs=1,
                             fixed_options=dict(cov=cov, run_option="climaf,scripts"))
else:
    launch_several_processes(run_coverage, list_values=args.run_modules, max_procs=1,
                             fixed_options=dict(cov=cov, run_option="{},scripts"))

# Remove macro file
os.remove(climaf_macro_file)

# Assemble coverage results
cov.combine()

# Make html coverage results
cov.html_report(title="CliMAF unitests coverage", directory=html_report_dir)
