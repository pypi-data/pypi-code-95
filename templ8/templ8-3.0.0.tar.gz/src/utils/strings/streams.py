def indent_lines(string: str, indent: str) -> str:
    return indent + string.replace("\n", "\n" + indent) if string else ""


def truncate_lines(string: str, limit: int) -> str:
    return "\n".join(
        [
            line[:limit] + "..." if len(line) > limit else line
            for line in string.split("\n")
        ]
    )
