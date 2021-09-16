from flask_log_request_id import current_request_id


def adscale_log(
    service: str,  # should be ValueOf ServiceEnum
    msg: str
    ):
    request_id = None
    try:
        request_id = current_request_id()
    except KeyError:
        pass

    print(f"[{service}][{request_id}] {msg}")
