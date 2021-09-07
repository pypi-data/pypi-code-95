#!/usr/bin/env python3


from typing import Any, Dict, Union


class CFError(Exception):
    ...


class APIError(CFError):
    def __init__(self, errors: Union[Dict[str, Any], str], *args, **kargs) -> None:
        if isinstance(errors, list):
            for error in errors:
                self.code = error["code"]
                self.message = error["message"]
                super().__init__(self.message, *args, **kargs)
        elif isinstance(errors, dict):
            self.code = errors["code"]
            self.message = errors["error"]
            super().__init__(self.message, *args, **kargs)
        else:
            raise CFError("Unknown internal error")

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
