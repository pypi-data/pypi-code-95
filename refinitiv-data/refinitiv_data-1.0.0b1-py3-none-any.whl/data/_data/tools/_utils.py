import re

pattern_1 = re.compile("(.)([A-Z][a-z]+)")
pattern_2 = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake(s):
    if not s:
        return s

    if "_" in s:
        words = [camel_to_snake(w) for w in s.split("_")]
        s = "_".join(words)

    else:
        s = pattern_1.sub(r"\1_\2", s)
        s = pattern_2.sub(r"\1_\2", s)

    return s.lower()
