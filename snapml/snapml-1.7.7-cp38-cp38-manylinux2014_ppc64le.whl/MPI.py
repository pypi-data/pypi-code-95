# *****************************************************************
#
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2018, 2019. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# *****************************************************************

import sys

if sys.version_info[0] < 3:
    import libsnapmlmpi2 as libsnapmlmpi
else:
    import snapml.libsnapmlmpi3 as libsnapmlmpi


def Comm_get_info():
    """
    Function for extracting the MPI communicator size and the rank ID.

    Returns
    -------
    (comm_size, rank_id) : (int, int)
        Returns the MPI communicator size and the rank ID of the calling
        MPI process.
    """
    (comm_size, rank) = libsnapmlmpi.MPI_get_info()
    return (comm_size, rank)
