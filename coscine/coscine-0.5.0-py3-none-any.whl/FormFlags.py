###############################################################################
# Coscine Python3 Client
# Copyright (c) 2018-2021 RWTH Aachen University
# Contact: coscine@itc.rwth-aachen.de
# Git: https://git.rwth-aachen.de/coscine/docs/public/wiki/-/tree/master/
# Please direct bug reports, feature requests or questions at the URL above
# by opening an issue.
###############################################################################
# This python wrapper implements a client for the Coscine API.
# Coscine is an open source project at RWTH Aachen University for
# the management of research data.
# Visit https://coscine.rwth-aachen.de for more information.
###############################################################################

from enum import IntFlag

class FormFlags(IntFlag):
	NONE = 0x0
	REQUIRED = 0x1
	CONTROLLED = 0x2
	SET = 0x4
	FIXED = 0x8