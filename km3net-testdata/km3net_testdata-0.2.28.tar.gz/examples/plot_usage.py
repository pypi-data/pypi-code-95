"""
How to use the package
=======================

The following example shows how to use the `Calculator` class.
"""
from km3net_testdata import data_path

#####################################################
# Getting a filename
# ------------------
# To get the filename of a sample file:

filename = data_path("online/km3net_online.root")
print(filename)
