from __future__ import absolute_import, division, print_function, unicode_literals

# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""lvm.py: Module to manipulate LVM devices."""

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import re  # regex
import fileinput
from libsan.host.cmdline import run


def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


###########################################
# PV section
###########################################
def pv_query(verbose=False):
    """Query Physical Volumes and return a dictonary with PV information for each PV.
    The arguments are:
    \tNone
    Returns:
    \tdict: Return a dictionary with PV info for each PV
    """
    cmd = "pvs --noheadings --separator \",\""
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("INFO: there is no VGs")
        return None
    pvs = output.split("\n")

    # format of PV info: PV,VG,Fmt,Attr,PSize,PFree
    pv_info_regex = r"\s+(\S+),(\S+)?,(\S+),(.*),(.*),(.*)$"

    pv_dict = {}
    for pv in pvs:
        m = re.match(pv_info_regex, pv)
        if not m:
            # _print("WARN: (%s) does not match vgdisplay output format" % vg)
            continue
        pv_info_dict = {"vg": m.group(2),
                        "fmt": m.group(3),  # not sure what it is
                        "attr": m.group(4),
                        "psize": m.group(5),
                        "pfree": m.group(6)}
        pv_dict[m.group(1)] = pv_info_dict

    return pv_dict


def pv_create(pv_name, options=None, verbose=True):
    """Create a Volume Group.
    The arguments are:
    \tPV name
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if options is None:
        options = ""

    if not pv_name:
        _print("FAIL: pv_create requires pv_name")
        return False
    cmd = "pvcreate %s %s" % (options, pv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        # _print ("FAIL: Could not create %s" % pv_name)
        return False
    return True


def pv_remove(pv_name, force=None, verbose=True):
    """Delete a Volume Group.
    The arguments are:
    \tVG name
    \tforce (boolean)
    \tverbose (boolean)
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t\tFalse in case of failure
    """
    if not pv_name:
        _print("FAIL: pv_remove requires pv_name")
        return False

    pv_dict = pv_query()

    pv_names = pv_name.split()
    for pv_name in pv_names:
        if pv_name not in list(pv_dict.keys()):
            _print("INFO: pv_remove - %s does not exist. Skipping..." % pv_name)
            return True

        options = ""
        if force:
            options += "--force --force"
        cmd = "pvremove %s %s" % (options, pv_name)
        retcode = run(cmd, verbose=verbose)
        if retcode != 0:
            _print("FAIL: Could not delete %s" % pv_name)
            return False
    return True


###########################################
# VG section
###########################################

def vg_show():
    """Show information for Volume Groups
    The arguments are:
    \tNone
    Returns:
    \tTrue
    or
    \tFalse
    """
    cmd = "vgs -a"
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: Could not show VGs")
        return False
    return True


def vg_query(verbose=False):
    """Query Volume Groups and return a dictonary with VG information for each VG.
    The arguments are:
    \tNone
    Returns:
    \tdict: Return a dictionary with VG info for each VG
    """
    cmd = "vgs --noheadings --separator \",\""
    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("INFO: there is no VGs")
        return None
    vgs = output.split("\n")

    # format of VG info: name #PV #LV #SN Attr VSize VFree
    vg_info_regex = r"\s+(\S+),(\S+),(\S+),(.*),(.*),(.*),(.*)$"

    vg_dict = {}
    for vg in vgs:
        m = re.match(vg_info_regex, vg)
        if not m:
            # _print("WARN: (%s) does not match vgdisplay output format" % vg)
            continue
        vg_info_dict = {"num_pvs": m.group(2),
                        "num_lvs": m.group(3),
                        "num_sn": m.group(4),  # not sure what it is
                        "attr": m.group(5),
                        "vsize": m.group(6),
                        "vfree": m.group(7)}
        vg_dict[m.group(1)] = vg_info_dict

    return vg_dict


def vg_create(vg_name, pv_name, force=False, verbose=True):
    """Create a Volume Group.
    The arguments are:
    \tPV name
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if not vg_name or not pv_name:
        _print("FAIL: vg_create requires vg_name and pv_name")
        return False

    options = ""
    if force:
        options += "--force"
    cmd = "vgcreate %s %s %s" % (options, vg_name, pv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        # _print ("FAIL: Could not create %s" % vg_name)
        return False
    return True


def vg_remove(vg_name, force=False, verbose=True):
    """Delete a Volume Group.
    The arguments are:
    \tVG name
    \tforce (boolean)
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if not vg_name:
        _print("FAIL: vg_remove requires vg_name")
        return False

    vg_dict = vg_query()
    if vg_name not in list(vg_dict.keys()):
        _print("INFO: vg_remove - %s does not exist. Skipping..." % vg_name)
        return True

    options = ""
    if force:
        options += "--force"
    cmd = "vgremove %s %s" % (options, vg_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        # _print ("FAIL: Could not delete %s" % vg_name)
        return False
    return True


###########################################
# LV section
###########################################

def lv_show():
    """
    Show information for Logical Volumes
    The arguments are:
    \tNone
    Returns:
    \tTrue
    or
    \tFalse
    """
    cmd = "lvs -a"
    retcode = run(cmd)
    if retcode != 0:
        _print("FAIL: Could not show LVs")
        return False
    return True


def lv_query(options=None, verbose=False):
    """Query Logical Volumes and return a dictonary with LV information for each LV.
    The arguments are:
    \toptions:  If not want to use default lvs output. Use -o for no default fields
    Returns:
    \tdict: Return a list with LV info for each LV
    """
    # Use \",\" as separator, as some output might contain ','
    # For example, lvs -o modules on thin device returns "thin,thin-pool"
    cmd = "lvs -a --noheadings --separator \\\",\\\""

    # format of LV info: Name VG Attr LSize Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
    lv_info_regex = r"\s+(\S+)\",\"(\S+)\",\"(\S+)\"" \
                    r",\"(\S+)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)$"

    # default parameters returned by lvs -a
    param_names = ["name", "vg_name", "attr", "size", "pool", "origin", "data_per", "meta_per", "move", "log",
                   "copy_per", "convert"]

    if options:
        param_names = ["name", "vg_name"]
        # need to change default regex
        lv_info_regex = r"\s+(\S+)\",\"(\S+)"
        parameters = options.split(",")
        for param in parameters:
            lv_info_regex += "\",\"(.*)"
            param_names.append(param)
        lv_info_regex += "$"
        cmd += " -o lv_name,vg_name,%s" % options

    retcode, output = run(cmd, return_output=True, verbose=verbose)
    if retcode != 0:
        _print("INFO: there is no LVs")
        return None
    lvs = output.split("\n")

    lv_list = []
    for lv in lvs:
        m = re.match(lv_info_regex, lv)
        if not m:
            _print("FAIL: (%s) does not match lvs output format" % lv)
            continue
        lv_info_dict = {}
        for index in range(len(param_names)):
            lv_info_dict[param_names[index]] = m.group(index + 1)
        lv_list.append(lv_info_dict)

    return lv_list


def lv_create(vg_name, lv_name, options="", verbose=True):
    """Create a Logical Volume.
    The arguments are:
    \tVG name
    \tLV name
    \toptions
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if not vg_name or not lv_name:
        _print("FAIL: lv_create requires vg_name and lv_name")
        return False

    cmd = "lvcreate %s %s -n %s" % (" ".join(str(i) for i in options), vg_name, lv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        # _print ("FAIL: Could not create %s" % lv_name)
        return False
    return True


def lv_info(lv_name, vg_name, options=None, verbose=False):
    """
    Show information of specific LV
    """
    if not lv_name or not vg_name:
        _print("FAIL: lv_info() - requires lv_name and vg_name as parameters")
        return None

    lvs = lv_query(options=options, verbose=verbose)

    if not lvs:
        return None

    for lv in lvs:
        if (lv["name"] == lv_name and
                lv["vg_name"] == vg_name):
            return lv
    return None


def lv_activate(lv_name, vg_name, verbose=True):
    """Activate a Logical Volume
    The arguments are:
    \tLV name
    \tVG name
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse if something went wrong
    """
    if not lv_name or not vg_name:
        _print("FAIL: lv_activate requires lv_name and vg_name")
        return False

    cmd = "lvchange -ay %s/%s" % (vg_name, lv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not activate LV %s" % lv_name)
        return False

    # Maybe we should query the LVs and make sure it is really activated
    return True


def lv_deactivate(lv_name, vg_name, verbose=True):
    """Deactivate a Logical Volume
    The arguments are:
    \tLV name
    \tVG name
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse if something went wrong
    """
    if not lv_name or not vg_name:
        _print("FAIL: lv_deactivate requires lv_name and vg_name")
        return False

    cmd = "lvchange -an %s/%s" % (vg_name, lv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not deactivate LV %s" % lv_name)
        return False

    # Maybe we should query the LVs and make sure it is really deactivated
    return True


def lv_remove(lv_name, vg_name, verbose=True):
    """Remove an LV from a VG
    The arguments are:
    \tLV name
    \tVG name
    Returns:
    \tBoolean:
    \t\tTrue in case of success
    \t\tFalse if something went wrong
    """
    if not lv_name or not vg_name:
        _print("FAIL: lv_remove requires lv_name and vg_name")
        return False

    lv_names = lv_name.split()

    for lv_name in lv_names:
        if not lv_info(lv_name, vg_name):
            _print("INFO: lv_remove - LV %s does not exist. Skipping" % lv_name)
            continue

        cmd = "lvremove --force %s/%s" % (vg_name, lv_name)
        retcode = run(cmd, verbose=verbose)
        if retcode != 0:
            _print("FAIL: Could not remove LV %s" % lv_name)
            return False

        if lv_info(lv_name, vg_name):
            _print("INFO: lv_remove - LV %s still exists." % lv_name)
            return False

    return True


def lv_convert(vg_name, lv_name, options, verbose=True):
    """Change Logical Volume layout.
    The arguments are:
    \tVG name
    \tLV name
    \toptions
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if not options:
        _print("FAIL: lv_convert requires at least some options specified.")
        return False

    if not lv_name or not vg_name:
        _print("FAIL: lv_convert requires vg_name and lv_name")
        return False

    cmd = "lvconvert %s %s/%s" % (" ".join(options), vg_name, lv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not convert %s" % lv_name)
        return False

    return True


def lv_extend(vg_name, lv_name, options, verbose=True):
    """Increase size of logical volume.
    The arguments are:
    \tVG name
    \tLV name
    \toptions
    Returns:
    \tBoolean:
    \t\tTrue if success
    \t'tFalse in case of failure
    """
    if not options:
        _print("FAIL: lv_extend requires at least some options specified.")
        return False

    if not lv_name or not vg_name:
        _print("FAIL: lv_extend requires vg_name and lv_name")
        return False

    cmd = "lvextend %s %s/%s" % (" ".join(options), vg_name, lv_name)
    retcode = run(cmd, verbose=verbose)
    if retcode != 0:
        _print("FAIL: Could not extend %s" % lv_name)
        return False

    return True


###########################################
# Config file
###########################################


def get_config_file_path():
    return "/etc/lvm/lvm.conf"


def update_config(key, value):
    config_file = get_config_file_path()
    search_regex = re.compile(r"(\s*)%s(\s*)=(\s*)\S*" % key)
    search_regex_with_comment = re.compile(r"(\s*#\s*)%s(\s*)=(\s*)\S*" % key)
    for line in fileinput.input(config_file, inplace=1):
        m = search_regex.match(line)
        m_with_comment = search_regex_with_comment.match(line)
        if m:
            line = "%s%s = %s" % (m.group(1), key, value)
        if m_with_comment:
            line = "%s%s = %s" % (m_with_comment.group(1).replace("#", ""), key, value)
        # print saves the line to the file
        # need to remove new line character as print will add it
        line = line.rstrip('\n')
        print(line)
