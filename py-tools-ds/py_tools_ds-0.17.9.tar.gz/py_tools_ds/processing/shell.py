# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2016-2021  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import shlex
from subprocess import PIPE, Popen

__author__ = "Daniel Scheffler"


def subcall_with_output(cmd, v=False):
    """Execute external command and get its stdout, exitcode and stderr.

    :param cmd: a normal shell command including parameters
    :param v:   verbose mode (prints
    """
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode

    if v and exitcode:
        print('SUBCALL CMD:', cmd)
        print('SUBCALL OUT:', out)
        print('SUBCALL ERR:', err)
    return out, exitcode, err
