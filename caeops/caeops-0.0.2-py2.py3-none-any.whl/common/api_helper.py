import json


def parse_rest_api_response(response) -> dict:
    """
    Handles the response received from the CloudAEye SaaS REST API
    :param response:
    :return:
    """
    # When an error response arrives
    if response.status_code == 401:
        raise Exception("Session Expired. Please login again")
    elif not response.ok:
        err_response = response.json()
        err_message = err_response.get("error", response.text)
        if err_message == "jwt expired":
            raise Exception("Session Expired. Please login again")
        raise Exception(err_message)
    res_json = response.json()
    return res_json.get("data", "")


def generate_error_response_text(cmd_name):
    return f"An error occurred when executing '{cmd_name}' command"


def generate_error_response(err):
    """
    A utility function that generates error response to be displayed by the caeops commands
    :param err: Error message to be wrapped and displayed
    :return: The error message to the displayed
    """
    return json.dumps({"error": str(err)}, indent=2)
