import json
import importlib

import click

from dude.api import KafkaToolbox
from . import main


def _must_be_a_valid_nubium_schema_import(ctx, param, value):
    if value is not None:
        try:
            components = value.split(".")
            module = importlib.import_module(".".join(["nubium_schemas"] + components[0:-1]))
            return getattr(module, components[-1])
        except ImportError as exc:
            raise click.BadParameter(
                ctx=ctx, param=param, message=f'"{value}" is not a valid python attribute to import'
            ) from exc
    return value


def _require_schema_file_when_schema_not_prestent(ctx, param, value):
    if value is None and ctx.params["schema"] is None:
        raise click.MissingParameter(ctx=ctx, param=param, message="Required if --schema not present")
    return value


class BootstrapServerParamType(click.ParamType):
    name = "bootstrap_server"

    def convert(self, value, param, ctx):
        return value

    def split_envvar_value(self, rv):
        return rv.split(",")


pass_kafka_toolbox = click.make_pass_decorator(KafkaToolbox)


@main.group("topic")
@click.pass_context
@click.option(
    "--bootstrap-server", required=True, multiple=True, envvar="BOOTSTRAP_SERVER", type=BootstrapServerParamType()
)
@click.option("--kafka-username", envvar="KAFKA_USERNAME")
@click.option("--kafka-password", envvar="KAFKA_PASSWORD")
@click.option("--security-protocol", default="sasl_ssl")
@click.option("--sasl-mechanisms", default="PLAIN")
def topic_group(ctx, bootstrap_server, kafka_username, kafka_password, security_protocol, sasl_mechanisms):
    broker_config = {"bootstrap.servers": ",".join(bootstrap_server)}
    if kafka_username:
        broker_config["sasl.username"] = kafka_username
        broker_config["sasl.password"] = kafka_password
        broker_config["security.protocol"] = security_protocol
        broker_config["sasl.mechanisms"] = sasl_mechanisms
    ctx.obj = KafkaToolbox(broker_config)


@topic_group.command(name="create")
@pass_kafka_toolbox
@click.option("--topic", required=True)
@click.option("--num-partitions", type=int, default=1)
@click.option("--replication-factor", type=int, default=3)
def create_topic(kafka_toolbox, topic, num_partitions, replication_factor):
    kafka_toolbox.create_topic(topic, num_partitions=num_partitions, replication_factor=replication_factor)


@topic_group.command(name="delete")
@pass_kafka_toolbox
@click.option("--topic", required=True, multiple=True)
def delete_topic(kafka_toolbox, topic):
    kafka_toolbox.delete_topic(topic)


@topic_group.command(name="list")
@pass_kafka_toolbox
def list_topics(kafka_toolbox):
    for topic in kafka_toolbox.list_topics():
        click.echo(topic)


@topic_group.command(name="produce")
@pass_kafka_toolbox
@click.option("--topic", required=True)
@click.option("--message-file", required=True, type=click.File("r"))
@click.option(
    "--schema",
    callback=_must_be_a_valid_nubium_schema_import,
    help="Path to import schema from nubium_schemas Ex: people_stream.person_schema",
)
@click.option(
    "--schema-file",
    type=click.File("r"),
    help="File containing json representation of schema [required if not using --schema]",
    callback=_require_schema_file_when_schema_not_prestent,
)
@click.option("--schema-registry-url", required=True, envvar="SCHEMA_REGISTRY_URL", default="http://localhost:8081")
def produce_message(kafka_toolbox, topic, message_file, schema_registry_url, schema, schema_file):
    if schema:
        schema_dict = schema
    else:
        schema_dict = json.loads(schema_file.read())
    message = json.loads(message_file.read())
    kafka_toolbox.produce_message(topic, message=message, schema=schema_dict, schema_registry_url=schema_registry_url)


@topic_group.command(name="wipe")
@pass_kafka_toolbox
@click.option("--topic", required=True)
def wipe_topic(kafka_toolbox, topic):
    kafka_toolbox.wipe_topic(topic)
