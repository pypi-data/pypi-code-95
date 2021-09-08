# build-in imports
import 	json

# external imports
from 	loguru 			import logger


__all__ = ('unpack_payload_dict')


@logger.catch()
def unpack_payload_dict(payload):
	"""[This function will turn the object into a json.]

	Args:
		payload (object): [A list of objects of type models to be transformed into json.]

	Raises:
		Exception: [An error will be raised if it is not possible to convert to json.]

	Returns:
		[json]: [The converted json]
	"""
	try: 
		return json.dumps(payload, default = lambda o: o.__dict__) if not isinstance(payload, str) else payload
	except json.JSONDecodeError:
		raise Exception(f'{type(payload)} cannot be turned into a json')
