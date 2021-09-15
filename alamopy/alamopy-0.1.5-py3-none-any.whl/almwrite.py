##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2020, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
almwrite.py
Write a .alm file according to the grammar specified by ALAMO. Essentially
    changing the file passed in by the client to fit the syntax necesary for the
    ALAMO to parse through. 
"""
import almutils as almutils


def write_alm_file(opts):
    """
    Write a .alm file according to the grammar specified by ALAMO. Essentially
    changing the file passed in by the client to fit the syntax necesary for the
    ALAMO to parse through. 

    Args:
        opts: a dictionary containing various options for writing the file. See
            almopts and almain
    """

    # open the file the client has passed in to write into
    with open(opts["alm_file_name"], "w+") as alm_file:

        # Writing all options
        for entry_name in opts["entry_names"]:
            if opts[entry_name] is not None:
                # write into the file with the entries
                alm_file.write(almutils.format_entry(entry_name, opts))

        # Writing all sections
        for section_name in opts["section_names"]:
            if opts[section_name] is not None:
                # write into the file with the sections
                alm_file.write(almutils.format_section(section_name, opts))
