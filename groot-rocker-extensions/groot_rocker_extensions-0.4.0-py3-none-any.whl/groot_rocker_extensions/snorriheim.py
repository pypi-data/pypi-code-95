#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Helpers related to the snorriheim ppa.

https://launchpad.net/~d-stonier/+archive/ubuntu/snorriheim
"""

##############################################################################
# Imports
##############################################################################

##############################################################################
# Methods
##############################################################################


def add_ppa():
    """Command for adding the snorriheim ppa"""
    return "apt-add-repository ppa:d-stonier/snorriheim"
