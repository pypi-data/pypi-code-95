# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from io import BytesIO
from contrast.utils.decorators import fail_safely


@fail_safely("Failed to convert scope to environ.")
def scope_to_environ(scope):
    """
    Convert an asgi `scope` into a wsgi `environ` dict

    Copied from https://github.com/django/asgiref/blob/main/asgiref/wsgi.py
    and modified to our needs
    """
    environ = {
        "REQUEST_METHOD": scope["method"],
        "SCRIPT_NAME": scope.get("root_path", "").encode("utf8").decode("latin1"),
        "PATH_INFO": scope["path"].encode("utf8").decode("latin1"),
        "QUERY_STRING": scope["query_string"].decode("ascii"),
        "SERVER_PROTOCOL": "HTTP/{}".format(scope["http_version"]),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": scope.get("scheme", "http"),
        # TODO: PYT-1725
        # "wsgi.input": body,
        "wsgi.errors": BytesIO(),
        "wsgi.multithread": True,
        "wsgi.multiprocess": True,
        "wsgi.run_once": False,
    }
    # Get server name and port - required in WSGI, not in ASGI
    # TODO: PYT-1725
    # if "server" in scope:
    #     environ["SERVER_NAME"] = scope["server"][0]
    #     environ["SERVER_PORT"] = str(scope["server"][1])
    # else:
    environ["SERVER_NAME"] = "localhost"
    environ["SERVER_PORT"] = "80"

    # TODO: PYT-1725
    # if "client" in scope:
    environ["REMOTE_ADDR"] = scope["client"][0]

    # Go through headers and make them into environ entries
    for name, value in scope.get("headers", []):
        name = name.decode("latin1")
        # TODO: PYT-1725
        # if name == "content-length":
        #     corrected_name = "CONTENT_LENGTH"
        # elif name == "content-type":
        #     corrected_name = "CONTENT_TYPE"
        # else:
        corrected_name = "HTTP_{}".format(name.upper().replace("-", "_"))
        # HTTPbis say only ASCII chars are allowed in headers, but we latin1 just in case
        value = value.decode("latin1")
        # TODO: PYT-1725
        # if corrected_name in environ:
        #     value = environ[corrected_name] + "," + value
        environ[corrected_name] = value
    return environ
