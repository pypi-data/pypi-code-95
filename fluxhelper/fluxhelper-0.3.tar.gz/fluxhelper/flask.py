
"""
Tools for flask or any other server related stuff
"""

import time

from flask import jsonify


def makeResponse(data: dict = None, msg: str = "", status: int = 200):
    response = {
        "status": status,
        "msg": "ok" if status == 200 else msg,
        "data": data if data else {},
        "timestamp": int(time.time())
    }

    return jsonify(response), status
