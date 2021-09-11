import string
import click
from click import STRING


class CommentFormatter(string.Formatter):

    def get_value(self, key, args, kwargs):
        return key

    def format_field(self, value, default_value):
        return click.prompt(f"{value}", type=STRING, default=default_value)