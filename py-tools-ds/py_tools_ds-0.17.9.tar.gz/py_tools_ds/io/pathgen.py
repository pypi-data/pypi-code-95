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

import tempfile
import os

__author__ = "Daniel Scheffler"


def get_tempfile(ext=None, prefix=None, tgt_dir=None):
    """Return the path to a tempfile.mkstemp() file that can be passed to any function that expects a physical path.

    NOTE: The tempfile has to be deleted manually.

    :param ext:     file extension (None if None)
    :param prefix:  optional file prefix
    :param tgt_dir: target directory (automatically set if None)
    """
    prefix = 'py_tools_ds__' if prefix is None else prefix
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=ext, dir=tgt_dir)
    os.close(fd)
    return path


def get_generic_outpath(dir_out='', fName_out='', prefix='', ext='', create_outDir=True,
                        prevent_overwriting=False):
    """Generate an output path accourding to the given parameters.

    :param dir_out:             output directory
    :param fName_out:           output filename
    :param prefix:              a prefix for the output filename. ignored if fName_out is given
    :param ext:                 the file extension to use
    :param create_outDir:       whether to automatically create the output directory or not
    :param prevent_overwriting: whether to prevent that a output filename is chosen that already exist in the filesystem
    :return:
    """
    dir_out = dir_out if dir_out else os.path.abspath(os.path.curdir)
    if create_outDir and not os.path.isdir(dir_out):
        os.makedirs(dir_out)

    if not fName_out:
        fName_out = '%soutput' % prefix + ('.%s' % ext if ext else '')
        if prevent_overwriting:
            count = 1
            while os.path.exists(os.path.join(dir_out, fName_out)):
                if count == 1:
                    fName_out += str(count)
                else:
                    fName_out[-1] = str(count)

    return os.path.join(dir_out, fName_out)
