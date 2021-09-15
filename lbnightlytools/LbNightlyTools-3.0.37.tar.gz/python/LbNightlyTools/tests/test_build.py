###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
# Uncomment to disable the tests.
#__test__ = False

import os

from LbNightlyTools.Configuration import Slot, Project

from LbNightlyTools.tests.utils import TemporaryDir

from os.path import normpath, join, exists

from LbEnv import which

import nose

_testdata = normpath(join(*([__file__] + [os.pardir] * 4 + ['testdata'])))


def test_basic_build():
    with TemporaryDir():
        slot = Slot('slot', build_tool='echo')
        slot.projects.append(Project('Gaudi', 'HEAD', checkout='ignore'))
        slot.checkout()

        res = slot.clean()
        assert 'Gaudi' in res
        assert res['Gaudi'].returncode == 0
        assert 'clean' in res['Gaudi'].stdout

        res = slot.build()
        assert 'Gaudi' in res
        assert res['Gaudi'].returncode == 0
        assert 'build' in res['Gaudi'].stdout

        res = slot.test()
        assert 'Gaudi' in res
        assert res['Gaudi'].returncode == 0
        assert 'test' in res['Gaudi'].stdout


def test_make_build():
    dummy_src = join(_testdata, 'build_tests', 'orig', 'dummy', '.')
    with TemporaryDir(chdir=True):
        slot = Slot(
            'slot',
            build_tool='make',
            projects=[
                Project(
                    'dummy',
                    'head',
                    checkout='copy',
                    checkout_opts=dict(src=dummy_src))
            ])
        slot.checkout()

        res = slot.build()
        assert exists(join('dummy', 'Makefile'))
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== building all ===' in res['dummy'].stdout
        assert exists(join('dummy', 'all'))

        res = slot.test()
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== running tests ===' in res['dummy'].stdout
        assert exists(join('dummy', 'test_results'))

        res = slot.clean()
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== cleaning ===' in res['dummy'].stdout
        assert exists(join('dummy', 'Makefile'))
        assert not exists(join('dummy', 'all'))
        assert not exists(join('dummy', 'test_results'))


def test_cmt_build():
    if not which('cmt'):
        raise nose.SkipTest

    dummy_src = join(_testdata, 'artifacts', 'packs', 'src',
                     'TestProject.HEAD.testing-slot.src.zip')

    config = "x86_64-centos7-gcc9-opt"
    print 'platform:', config

    with TemporaryDir(chdir=True):
        slot = Slot(
            'slot',
            build_tool='cmt',
            projects=[
                Project(
                    'TestProject',
                    'HEAD',
                    checkout='unzip',
                    checkout_opts=dict(src=dummy_src))
            ],
            env=[
                "BINARY_TAG=" + config,
                "CMTCONFIG=${BINARY_TAG}",
            ])
        slot.checkout()

        proj_root = join('TestProject')
        with open(join(proj_root, 'Makefile'), 'a') as mkf:
            # the Makefile in TestProject does not include tests and purge
            mkf.write('test:\n'
                      '\t@echo === running tests ===\n'
                      'clean:\n'
                      '\tcd TestProjectSys/cmt; $(MAKE) clean\n'
                      '\t$(RM) -r InstallArea\n'
                      'purge: clean\n'
                      '\t$(RM) TestProjectSys/cmt/Makefile\n')

        res = slot.build()
        assert exists(join(proj_root, 'Makefile'))
        assert 'TestProject' in res
        assert res['TestProject'].returncode == 0
        assert exists(
            join(proj_root, 'TestProjectSys', config, 'HelloWorld.exe'))
        assert exists(join(proj_root, 'TestProjectSys', 'cmt', 'Makefile'))
        assert exists(
            join(proj_root, 'InstallArea', config, 'bin', 'HelloWorld.exe'))

        res = slot.test()
        assert 'TestProject' in res
        assert res['TestProject'].returncode == 0

        res = slot.clean()
        assert 'TestProject' in res
        assert res['TestProject'].returncode == 0
        assert not exists(
            join(proj_root, 'TestProjectSys', config, 'HelloWorld.exe'))
        assert not exists(join(proj_root, 'TestProjectSys', 'cmt', 'Makefile'))
        assert not exists(
            join(proj_root, 'InstallArea', config, 'bin', 'HelloWorld.exe'))


def test_cmake_build():
    dummy_src = join(_testdata, 'build_tests', 'orig', 'dummy', '.')
    with TemporaryDir(chdir=True):
        slot = Slot(
            'slot',
            build_tool='cmake',
            projects=[
                Project(
                    'dummy',
                    'head',
                    checkout='copy',
                    checkout_opts=dict(src=dummy_src))
            ])
        slot.checkout()

        res = slot.build()
        assert exists(join('dummy', '', 'Makefile'))
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== configure ===' in res['dummy'].stdout
        assert '=== building all ===' in res['dummy'].stdout
        assert '=== unsafe-install ===' in res['dummy'].stdout
        assert '=== post-install ===' in res['dummy'].stdout
        assert '=== cleaning ===' in res['dummy'].stdout
        assert exists(join('dummy', 'all-installed'))
        assert exists(join('dummy', 'cache_preload.cmake'))

        res = slot.test()
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== running tests ===' in res['dummy'].stdout
        assert exists(join('dummy', 'test_results'))

        res = slot.clean()
        assert 'dummy' in res
        assert res['dummy'].returncode == 0
        assert '=== purge ===' in res['dummy'].stdout
        assert exists(join('dummy', 'Makefile'))
        assert not exists(join('dummy', 'all'))
        assert not exists(join('dummy', 'test_results'))
