import click

from .data_type import PhpCompileResult
from .do_php import do_php_compile

__all__ = ["init_php_cli", "PhpCompileResult", "do_php_compile"]


def init_php_cli(main: click.Group):
    @main.command()
    def php():
        """
        PHP 编译测试
        """
        result = do_php_compile()
        print(f"php compile result: {result}")
