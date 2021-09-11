import asyncio
from typing import Text

import click

from neuralspace.apis import get_async_http_session
from neuralspace.constants import NER_TYPES
from neuralspace.ner.apis import get_ner_response
from neuralspace.ner.constants import SUPPORTED_LANGUAGES
from neuralspace.utils import get_entity_list, setup_logger


@click.group(name="ner")
def ner():
    pass


@ner.command(
    name="parse",
)
@click.option(
    "-t",
    "--text",
    type=click.STRING,
    required=True,
    help="text to be parsed",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    required=True,
    help="language that the text was in",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def parse(text: Text, language: Text, log_level: Text):
    setup_logger(log_level=log_level)
    if not language:
        ValueError(f"Language is mandatory. You can select from {SUPPORTED_LANGUAGES}")
    if not text:
        ValueError("Please enter the text to parse")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(get_ner_response(text, language))
    loop.run_until_complete(get_async_http_session().close())


@ner.command(name="get-pretrained-entities")
@click.option("-L", "--language", type=click.STRING, required=True)
@click.option("-s", "--search", type=click.STRING, default="")
@click.option("-p", "--page-number", type=click.INT, default=1)
@click.option("-P", "--page-size", type=click.INT, default=5)
@click.option(
    "-T", "--entity-type", type=click.Choice(NER_TYPES), default="pre-trained"
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def get_pretrained_entities(
    language: Text,
    search: Text,
    page_number: int,
    page_size: int,
    entity_type: Text,
    log_level: Text,
):
    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        get_entity_list(language, search, page_number, page_size, entity_type)
    )
    loop.run_until_complete(get_async_http_session().close())
