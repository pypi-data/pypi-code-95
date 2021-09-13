import requests
import json
import warnings
import os

SERVER = os.getenv('WAMP_SERVER', "192.168.1.2")
BASE_URL = "http://{}:8080/".format(SERVER)
CALL_URL = BASE_URL + "call"
PUBLISH_URL = BASE_URL + "publish"


class WAMPRuntimeError(Exception):
    pass


def _send(url, destination, *args, **kwargs):
    json_key = 'procedure' if url == CALL_URL else 'topic'
    json = {json_key: destination}
    if args:
        json['args'] = args
    if kwargs:
        json['kwargs'] = kwargs
    response = requests.post(url, json=json)
    response.raise_for_status()
    return response.content.decode()


def _check_procedure(procedure):
    """
    Check if remote procedures registered with server
    """
    data = json.loads(_send(CALL_URL, 'wamp.registration.lookup', procedure))
    return bool(data['args'][0])


def _check_topic(topic):
    """
    Check if anyone has subscribed to this topic on server
    """
    data = json.loads(_send(CALL_URL, 'wamp.subscription.lookup', topic))
    return bool(data['args'][0])


def call(procedure, *args, **kwargs):
    """
    Call a remote procedure that has been registered with the server

    Parameters
    ----------
    procedure : str
        name of procedure, e.g 'hipercam.Compo.rpc.power_off_axis'
    *args : (optional) variable length argument list
        arguments to pass to remote procedure
    **kwargs : (optional)
        dictionary of kwargs to pass to remote procedure

    Returns
    -------
    result
        the result of calling the remote procedure
    """
    if not _check_procedure(procedure):
        raise ValueError('procedure "{}" not registered with WAMP server'.format(
            procedure))
    response = json.loads(_send(CALL_URL, procedure, *args, **kwargs))
    if "error" in response:
        raise WAMPRuntimeError(
            response['args']
        )
    return response['args'][0]


def publish(topic, *args, **kwargs):
    """
    Publish data to a topic

    The routine will warn, but not fail, if no-one is subscribed to the topic

    Parameters
    ----------
    topic : str
        name of topic, e.g 'hipercam.FocalPlaneSlide.target_position'
    *args : (optional) variable length argument list
        arguments to publish to topic
    **kwargs : (optional)
        dictionary of kwargs to publish to topic

    Returns
    -------
    result
        the response from the server
    """
    if not _check_topic(topic):
        warnings.warn(
            'no-one has subscribed to topic {}. your message may not be read'.format(
                topic
            )
        )

    response = json.loads(_send(PUBLISH_URL, topic, *args, **kwargs))
    msg_id = response['id']
    return msg_id
