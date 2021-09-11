import logging
import time
from typing import Optional

import typer

from . import __version__
from .mqtt_task import mqttc_setup, mqttc_publish, mqttc_close

# config logging in main
LOG_SIMPLE = "%(asctime)s | %(levelname).1s | %(name)s | %(message)s"
LOG_PROCESS = "%(asctime)s | %(levelname).1s | %(processName)s | %(name)s | %(message)s"
LOG_THREAD = "%(asctime)s | %(levelname).1s | %(threadName)s | %(name)s | %(message)s"
logging.basicConfig(
    level="INFO",
    format=LOG_THREAD,
)
# get logger
log = logging.getLogger(__name__)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.secho(f"CLI Version: {__version__}", fg=typer.colors.MAGENTA)
        raise typer.Exit()


# Main command
@app.command()
def main(
    _version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
    log_level: str = typer.Option("INFO", envvar="LOG_LEVEL", help="log level"),
    mqtt_broker: str = typer.Option(
        ..., "--broker", "-b", envvar="MQTT_BROKER", help="The Hostname/IP of MQTT broker"
    ),
    mqtt_port: int = typer.Option(1883, "--port", "-p", envvar="MQTT_PORT", help="The port of MQTT broker"),
    mqtt_username: str = typer.Option(
        "", "--username", "-u", envvar="MQTT_USERNAME", help="The name of MQTT user"
    ),
    # mqtt_password: str = typer.Option("", "--password", envvar="MQTT_PASSWORD", prompt=True, hide_input=True),
    mqtt_password: str = typer.Option(
        "", "--password", envvar="MQTT_PASSWORD", help="The password of MQTT user"
    ),
    mqtt_qos: int = typer.Option(0, "--qos", "-q", envvar="MQTT_QOS", help="QoS value for MQTT"),
    mqtt_debug: bool = typer.Option(False, "--debug", "-d", help="debug mqtt"),
):
    """
    A CLI app to handle mqtt
    """
    typer.echo(f"{__name__} starting...")
    if log_level:
        log.setLevel(log_level)
        typer.echo(f"set logging level to {log_level}")
    log.info(f"{__name__} started.")
    log.debug(f"mqtt_broker = {mqtt_broker}")
    log.debug(f"mqtt_port = {mqtt_port}")
    if mqtt_username:
        log.debug(f"mqtt_username = {mqtt_username}")
    log.debug(f"mqtt_debug = {mqtt_debug}")

    # Setup mqtt
    mqttc_setup(mqtt_broker, mqtt_port, mqtt_username, mqtt_password, mqtt_qos)

    # main loop
    run_flag = True
    interval_s = 3.0
    last_check = 0
    while run_flag:
        now = time.time()
        if last_check == 0:
            last_check = now
            continue
        # routine check
        if now > last_check + interval_s:
            mqttc_publish("ysdtest/1", f"hello, {now}")
            last_check = now

    mqttc_close()


if __name__ == "__main__":
    app()
