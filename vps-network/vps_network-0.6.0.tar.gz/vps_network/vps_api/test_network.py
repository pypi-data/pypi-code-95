import os

from .dt import PingForm, SpeedForm, ServerListForm, TraceForm
from .network import NetworkApi


def get_app_key() -> str:
    """
    on github CI read from env
    """
    app_key = os.getenv("VPS_API_KEY", None)
    if app_key is not None:
        return app_key

    app_key_file = os.path.join(os.path.dirname(__file__), "../../app_key.txt")
    with open(app_key_file) as fp:
        content = fp.read()
        return content.strip()


def test_server_list():
    api = NetworkApi()
    server_list = api.server_list(ServerListForm(limit=1))
    assert len(server_list) == 1


def test_ping_report():
    app_key = get_app_key()
    api = NetworkApi(app_key=app_key)
    form = PingForm(results=[])
    ret = api.ping_report(form)
    assert ret.errno == 0


def test_speed_report():
    app_key = get_app_key()
    api = NetworkApi(app_key=app_key)
    form = SpeedForm(results=[])
    ret = api.speed_report(form)
    assert ret.errno == 0


def test_trace_report():
    app_key = get_app_key()
    api = NetworkApi(app_key=app_key)
    form = TraceForm(results=[])
    ret = api.trace_report(form)
    assert ret.errno == 0
