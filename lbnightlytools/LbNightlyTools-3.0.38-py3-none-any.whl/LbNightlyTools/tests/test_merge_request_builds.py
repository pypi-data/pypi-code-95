##############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from nose import with_setup
from nose.tools import assert_raises

from LbNightlyTools.Configuration import slots, Slot, Project, DBASE, Package
from LbNightlyTools.MergeRequestBuilds import create_mr_slots


def create_master_slot():
    return Slot(
        "lhcb-master",
        projects=[
            Project("Detector", "v0-patches"),
            Project("LHCb", "master"),
            Project("Lbcom", "master"),
            Project("Rec", "master"),
            DBASE(packages=[Package('PRConfig', 'HEAD')]),
        ],
        platforms=['x86_64-centos7-gcc9-opt'])


@with_setup(slots.clear, slots.clear)
def test_branch_mode():
    model_slot = create_master_slot()
    model_slots = [model_slot]

    with assert_raises(ValueError):
        create_mr_slots(["lhcb/Rec!1753", "lhcb/Rec!1755"],
                        platforms=None,
                        merge=False,
                        model_slots=model_slots)

    ref_slot, test_slot = create_mr_slots(["lhcb/Rec!1753"],
                                          platforms=None,
                                          merge=False,
                                          model_slots=model_slots)

    assert (ref_slot.projects['Detector'].checkout_opts['commit'] ==
            test_slot.projects['Detector'].checkout_opts['commit'] ==
            'b8b797e6496307132af05b4d2be29d7ee9416ad1')

    assert (ref_slot.projects['LHCb'].checkout_opts['commit'] ==
            test_slot.projects['LHCb'].checkout_opts['commit'] ==
            'a41659c4ad4113c83d3a7789679228219057c921')

    assert (ref_slot.projects['Rec'].checkout_opts['commit'] ==
            '14f25f03810120eaae280e1f6b38e86a87f00b38')

    assert (test_slot.projects['Rec'].checkout_opts['commit'] ==
            '414ae00f32e2f738eb935e6a1847b010a087586c')


@with_setup(slots.clear, slots.clear)
def test_integration_mode():
    model_slot = create_master_slot()
    model_slots = [model_slot]

    ref_slot, test_slot = create_mr_slots(
        [
            "lhcb/LHCb@2ad1a811",  # a commit
            "lhcb/Rec!1755",
            "lhcb/Rec!1753",  # multiple MRs per project
            "lhcb-datapkg/PRConfig!135",  # a data package
            "lhcb-datapkg/AppConfig!100",  # a data package not in model
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots)

    # the reference slot does not checkout commits or merge MRs
    assert all(not p.checkout_opts for p in ref_slot.projects)

    assert (test_slot.projects['LHCb'].checkout_opts['commit'] ==
            '2ad1a8118eb04037fde5d9c522fb169de96f80bb')
    assert (not test_slot.projects['Lbcom'].checkout_opts)
    assert (test_slot.projects['Rec'].checkout_opts == {
        'merges': [1755, 1753]
    })
    assert (test_slot.projects['DBASE'].packages['PRConfig'].checkout_opts == {
        'merges': [135]
    })
    assert (
        test_slot.projects['DBASE'].packages['AppConfig'].checkout_opts == {
            'merges': [100]
        })
