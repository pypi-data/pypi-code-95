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

class CoscineException(Exception):
	pass

class ConnectionError(CoscineException):
	pass

class ServerError(CoscineException):
	pass

class VocabularyError(CoscineException):
	pass

class RequirementError(CoscineException):
	pass

class UnauthorizedError(CoscineException):
	pass