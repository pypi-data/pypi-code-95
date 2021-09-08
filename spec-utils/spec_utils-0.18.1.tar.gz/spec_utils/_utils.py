import re
from random import choice as r_choice
from string import digits as str_digits, ascii_lowercase as str_letters
from typing import Callable, Any, Optional

class Decorators:
    @staticmethod
    def ensure_session(method: Callable) -> Callable:
        def wrapper(client, *args, **kwargs) -> Optional[Any]:
            if client.session == None:
                raise ConnectionError(f"""
                    Start a session with self.start_session() before of make a 
                    request or use "with" expression like with 
                    {client.__class__.__name__}(url=...) as client: ...
                """)
            return method(client, *args, **kwargs)
        return wrapper


def random_str(
    size: Optional[int] = 5,
    chars: Optional[str] = str_digits + str_letters
) -> str:
    """ Return a str of 'size' len with numbers and ascii lower letters. """

    return ''.join(r_choice(chars) for _ in range(size))


def create_random_suffix(name: Optional[str] = "") -> str:
    """ Create a random name adding suffix after of clean recived name. """

    clean = re.sub('[^a-zA-Z0-9]', '_', name)
    clean += '_' if name else "" 
    clean += random_str(size=5)

    return clean