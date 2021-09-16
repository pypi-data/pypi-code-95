# build-in imports
from dataclasses	import dataclass

# external imports
from loguru 	import logger
from requests 	import Response


@dataclass
class AttemptRequests:
	"""[This decorator's function is to manage the callback of requests,
	everything that is not in success_status will pass a trial, and if
	the attempts are exceeded, an error will be raised.]

	Args:
		success_codes ((list, int), optional): [An int list or an int with the allowed status codes.]. Defaults to [200].
		attempts (int, optional): [number of attempts.]. Defaults to 3.
		debug (bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If success_code is not of type int or a list of int, it will raise an Exception.]
		Exception: [If the attempts are exceeded will raise an Exception.]
		TypeError: [If the function's return is not a requests type, it will raise a TypeError.]

	Returns:
		[requests.Response]: [It will return a Response from the requests.]
	"""
	success_codes	: int		= 200
	attempts		: int 		= 3

	def __call__(self, func, *args, **kwargs):
		@logger.catch()
		def inner(*args, attempt=1, **kwargs):
			if not isinstance(self.success_codes, (int, list)):
				raise TypeError('Please pass in a valid success_code, it must be of type int or a list of int')

			if isinstance(self.success_codes, int):
				self.success_codes = [self.success_codes]

			if attempt > self.attempts:
				raise Exception('Function exceeded retries. Check the logs for more information.')

			print(func)

			resp = func(*args, **kwargs)
			if not isinstance(resp, Response):
				raise TypeError('This function does not have a request return, please use this decorator with requests only.')

			logger.debug(f'URL: {resp.url}')
			logger.debug(f'STATUS: {resp.status_code}')
			logger.debug(f'ELAPSED: {resp.elapsed}')
			logger.debug(f'ENCODING: {resp.encoding}')
			logger.debug(f'APPARENT ENCODING: {resp.apparent_encoding}')
			logger.debug(f'HEADERS: {resp.headers}')
			logger.debug(f'COOKIES: {resp.cookies}')
			logger.debug(f'BODY: {resp.content}')

			if resp.status_code not in self.success_codes:
				logger.error(f"[{attempt}]Attempt: {resp.url} - Failed - [{resp.status_code}]{resp.content}")
				inner(*args, attempt=attempt+1, **kwargs)

			logger.success(f"[{attempt}]Attempt: {resp.url}")
			return resp
		return inner
