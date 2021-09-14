class TimeoutException(Exception):
	"""Exception for timeout errors."""
	def __init__(self, message: str):
		super(TimeoutException, self).__init__(message)


class StatusException(Exception):
	"""Exception for instrument status errors."""
	def __init__(self, rsrc_name: str, message: str):
		self.rsrc_name = rsrc_name
		super(StatusException, self).__init__(message)


class UnexpectedResponseException(Exception):
	"""Exception for instrument unexpected responses."""
	def __init__(self, rsrc_name: str, message: str):
		self.rsrc_name = rsrc_name
		super(UnexpectedResponseException, self).__init__(message)


def assert_no_instrument_status_errors(rsrc_name: str, errors: list, context: str = '') -> None:
	"""Checks the errors list and of it contains at least one element, it throws StatusException."""
	if errors is None:
		return
	if len(errors) == 0:
		return
	if context:
		message = f"'{rsrc_name}': {context} "
	else:
		message = f"'{rsrc_name}': "
	if len(errors) == 1:
		message += f'Instrument error detected: {errors[0]}'
		raise StatusException(rsrc_name, message)
	if len(errors) > 1:
		message += '{} Instrument errors detected:\n{}'.format(len(errors), '\n'.join(errors))
		raise StatusException(rsrc_name, message)
