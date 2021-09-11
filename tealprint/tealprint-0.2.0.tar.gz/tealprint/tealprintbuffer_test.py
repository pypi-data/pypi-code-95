import pytest

from . import TealConfig, TealLevel, TealPrintBuffer

indent = "".ljust(TealConfig.indent_by, TealConfig.indent_char)


class T:
    logger = TealPrintBuffer()

    @staticmethod
    def reset():
        TealConfig.level = TealLevel.info
        T.logger = TealPrintBuffer()


@pytest.mark.parametrize(
    "name,expected,function",
    [
        (
            "Not indented by default",
            "test\n",
            lambda: T.logger.info("test"),
        ),
        (
            "Indented when when pushed with same lever",
            f"{indent}test\n",
            lambda: (
                T.logger.push_indent(TealLevel.info),
                T.logger.info("test"),
            ),
        ),
        (
            "Indented when when pushed with higher lever",
            f"{indent}test\n",
            lambda: (
                T.logger.push_indent(TealLevel.warning),
                T.logger.info("test"),
            ),
        ),
        (
            "Not Indented when when pushed with same lever",
            f"test\n",
            lambda: (
                T.logger.push_indent(TealLevel.verbose),
                T.logger.info("test"),
            ),
        ),
        (
            "Indented when when pushed in info()",
            f"first\n{indent}test\n",
            lambda: (
                T.logger.info("first", push_indent=True),
                T.logger.info("test"),
            ),
        ),
        (
            "Don't de-indent after pop if level is lower than current",
            f"{indent}test\n{indent}test\ntest\n",
            lambda: (
                T.logger.push_indent(TealLevel.info),
                T.logger.push_indent(TealLevel.verbose),
                T.logger.info("test"),
                T.logger.pop_indent(),
                T.logger.info("test"),
                T.logger.pop_indent(),
                T.logger.info("test"),
            ),
        ),
        (
            "No indent after cleaning",
            f"test\n",
            lambda: (
                T.logger.push_indent(TealLevel.info),
                T.logger.clear_indent(),
                T.logger.info("test"),
            ),
        ),
    ],
)
def test_indentation(name, expected: str, function) -> None:
    print(name)

    function()

    T.logger.buffer.seek(0)
    result = T.logger.buffer.read()
    assert expected == result

    T.reset()
