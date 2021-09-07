# -*- encoding: utf-8 -*-
# Folder Structure Creator v0.1.5
# A simple folder structure creator.
# Copyright © 2021, David Sanchez-Wells.
# See /LICENSE for licensing information.

"""
Folder Creator main entry-point (defaults to CLI).
:Copyright: © 2021, David Sanchez-Wells.
:License: BSD (see /LICENSE).
"""

import folder_structure.cli
import sys

__all__ = ()

if __name__ == '__main__':
    sys.exit(folder_structure.cli.main())
