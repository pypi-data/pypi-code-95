###############################################################################
# Coscine Python Client
# Copyright (c) 2018-2021 RWTH Aachen University
# Contact: coscine@itc.rwth-aachen.de
# Git: https://git.rwth-aachen.de/coscine/docs/public/coscine-python-client
# Please direct bug reports, feature requests or questions at the URL above
# by opening an issue.
###############################################################################
# Coscine is an open source project at RWTH Aachen University for
# the management of research data.
# Visit https://coscine.de for more information.
###############################################################################

###############################################################################
# This file provides the ProgressBar class - a simple wrapper around tqdm
# progress bars. It is used in download/upload methods and provides the
# benefit of remembering state information and printing only when in
# verbose mode.
###############################################################################

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from coscine.client import Client
from tqdm import tqdm

###############################################################################

class ProgressBar:

	def __init__(self, client: Client, filesize: int, filename: str, \
								mode: str, callafter: function = None):

		MODES = {
			"UP": "↑",
			"DOWN": "↓"
		}
		if mode not in MODES:
			raise ValueError(mode)

		self.client = client
		if client.verbose:
			self.bar = tqdm(total = filesize, unit = "B", unit_scale = True,
									desc = "%s %s" % (MODES[mode], filename))
		self.callafter = callafter
		self.n = 0

###############################################################################

	def update(self, chunksize: int):
		self.n += chunksize
		if self.client.verbose:
			self.bar.update(chunksize)
		if self.callafter:
			self.callafter(chunksize)

###############################################################################