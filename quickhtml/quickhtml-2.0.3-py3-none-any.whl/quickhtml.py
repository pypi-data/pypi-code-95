"""This file contains the main program functionality."""

import re

REGEX_BLOCKQUOTE = re.compile(r"""
    \s*         # Match between 0 and ∞ whitespaces.
    (>+)        # CAPTURE GROUP (1) | Match between 1 and ∞ ">".
    \s*         # Match between 0 and ∞ whitespaces.
    ([^>].*?)   # CAPTURE GROUP (2) | Match first character that is not ">",
                # then match between 0 and ∞ characters, as few times as
                # possible.
    \s*         # Match between 0 and ∞ whitespaces.""", re.VERBOSE)

REGEX_BOLD = re.compile(r"""
    (?<!\\)         # Ensure there's no escaping backslash.
    \*{2}           # Match "*" twice.
    ([^\s*].*?)     # CAPTURE GROUP (1) | Match first character that is not "*"
                    # or a whitespace, then match between 0 and ∞ characters,
                    # as few times as possible.
    (?<![\\\s*])    # Ensure there's no escaping backslash, whitespace, or "*".
    \*{2}           # Match "*" twice.
    |               # OR
    (?<!\\)         # Ensure there's no escaping backslash.
    _{2}            # Match "_" twice.
    ([^\s_].*?)     # CAPTURE GROUP (2) | Match first character that is not "_"
                    # or a whitespace, then match between 0 and ∞ characters,
                    # as few times as possible.
    (?<![\\\s_])    # Ensure there's no escaping backslash, whitespace, or "_".
    _{2}            # Match "_" twice.""", re.VERBOSE)

REGEX_CODE = re.compile(r"""
    (?<!\\)     # Ensure there's no escaping backslash.
    (?:         # Open non-capturing group.
        `{2}    # Match "`" twice.
        \s*     # Match between 0 and ∞ whitespaces.
        (.+?)   # CAPTURE GROUP (1) | Match between 1 and ∞ characters, as few
                # times as possible.
        \s*     # Match between 0 and ∞ whitespaces.
        (?<!\\) # Ensure there's no escaping backslash.
        `{2}    # Match "`" twice.
    )           # Close and match non-capturing group.
    |           # OR
    (?:         # Open non-capturing group.
        `       # Match "`" once.
        \s*     # Match between 0 and ∞ whitespaces.
        (.+?)   # CAPTURE GROUP (2) | Match between 1 and ∞ characters, as few
                # times as possible.
        \s*     # Match between 0 and ∞ whitespaces.
        (?<!\\) # Ensure there's no escaping backslash.
        `       # Match "`" once.
    )           # Close and match non-capturing group.
    (?=[^`]|$)  # Make sure there is a line end or a character other than "`"
                # ahead.""", re.VERBOSE)

REGEX_ESCAPED_CHARACTER = re.compile(r"""
    \\  # Match "\" once.
    (.) # CAPTURE GROUP (1) | Match any character once.""", re.VERBOSE)

REGEX_HEADING = re.compile(r"""
    ((?:^|>|-|[0-9]+[.\)])\s*)  # CAPTURE GROUP (1) | Match either line start,
                                # ">", "-", or a number followed by either "."
                                # or ")", then match between 0 and ∞
                                # whitespaces.
    (\#{1,6})                   # CAPTURE GROUP (2) | Match "#" between 1 and 6
                                # times.
    \s+                         # Match between 1 and ∞ whitespaces.
    ([^\s].*?)                  # CAPTURE GROUP (3) | Match first character
                                # that is not a whitespace, then match between
                                # 0 and ∞ characters, as few times as possible.
    (\s*)                       # CAPTURE GROUP (4) | Match between 0 and ∞
                                # whitespaces.
    $                           # Match line end.""", re.VERBOSE)

REGEX_HORIZONTAL_RULE = re.compile(r"""
    ^               # Match line start.
    \s*             # Match between 0 and ∞ whitespaces.
    (?:\*|-|_){3,}  # Match either "*", "-" or "_", at least 3 times.
    \s*             # Match between 0 and ∞ whitespaces.
    $               # Match line end.""", re.VERBOSE)

REGEX_IMAGE = re.compile(r"""
    (?<!\\)     # Ensure there's no escaping backslash.
    !           # Match "!" once.
    \[          # Match "[" once.
    \s*         # Match between 0 and ∞ whitespaces.
    (.+?)       # CAPTURE GROUP (2) | Match between 1 and ∞ characters, as few
                # times as possible.
    \s*         # Match between 0 and ∞ whitespaces.
    \]          # Match "]" once.
    \(          # Match "(" once.
    \s*         # Match between 0 and ∞ whitespaces.
    (.+?)       # CAPTURE GROUP (3) | Match between 1 and ∞ characters, as few
                # times as possible.
    \s*         # Match between 0 and ∞ whitespaces.
    (?:         # Open non-capturing group.
        [\"']   # Match either "'" or '"' once.
        \s*     # Match between 0 and ∞ whitespaces.
        (.+?)   # CAPTURE GROUP (4) | Match between 1 and ∞ characters, as few
                # times as possible.
        \s*     # Match between 0 and ∞ whitespaces.
        [\"']   # Match either "'" or '"' once.
    )?          # Close non-capturing group and match it either 0 or 1 times.
    \s*         # Match between 0 and ∞ whitespaces.
    \)          # Match ")" once.""", re.VERBOSE)

REGEX_ITALIC = re.compile(r"""
    (?<!\\)         # Ensure there's no escaping backslash.
    \*              # Match "*" once.
    ([^\s*].*?)     # CAPTURE GROUP (1) | Match first character that is not "*"
                    # or a whitespace, then match between 0 and ∞ characters,
                    # as few times as possible.
    (?<![\\\s*])    # Ensure there's no escaping backslash, whitespace, or "*".
    \*              # Match "*" once.
    |               # OR
    (?<!\\)         # Ensure there's no escaping backslash.
    _               # Match "_" once.
    ([^\s_].*?)     # CAPTURE GROUP (2) | Match first character that is not "_"
                    # or a whitespace, then match between 0 and ∞ characters,
                    # as few times as possible.
    (?<![\\\s_])    # Ensure there's no escaping backslash, whitespace, or "_".
    _               # Match "_" once.""", re.VERBOSE)

REGEX_LINK = re.compile(r"""
    (?<!\\)     # Ensure there's no escaping backslash.
    \[          # Match "[" once.
    \s*         # Match between 0 and ∞ whitespaces.
    (.+?)       # CAPTURE GROUP (1) | Match between 1 and ∞ characters, as few
                # times as possible.
    \s*         # Match between 0 and ∞ whitespaces.
    \]          # Match "]" once.
    \(          # Match "(" once.
    \s*         # Match between 0 and ∞ whitespaces.
    (.+?)       # CAPTURE GROUP (2) | Match between 1 and ∞ characters, as few
                # times as possible.
    \s*         # Match between 0 and ∞ whitespaces.
    (?:         # Open non-capturing group.
        [\"']   # Match either "'" or '"' once.
        \s*     # Match between 0 and ∞ whitespaces.
        (.+?)   # CAPTURE GROUP (3) | Match between 1 and ∞ characters, as few
                # times as possible.
        \s*     # Match between 0 and ∞ whitespaces.
        [\"']   # Match either "'" or '"' once.
    )?          # Close non-capturing group and match it either 0 or 1 times.
    \s*         # Match between 0 and ∞ whitespaces.
    \)          # Match ")" once.""", re.VERBOSE)

REGEX_ORDERED_LIST = re.compile(r"""
    (\s+)?  # CAPTURE GROUP (1) | Match between 1 and ∞ whitespaces, as many
            # times as possible, as either one or zero matches.
    [0-9]+  # Match between 1 and ∞ numbers.
    [.)]    # Match either "." or ")" once.
    \s+     # Match between 1 and ∞ whitespaces.
    (.+?)   # CAPTURE GROUP (2) | Match between 1 and ∞ characters, as few
            # times as possible.
    \s*     # Match between 0 and ∞ whitespaces.""", re.VERBOSE)

REGEX_UNORDERED_LIST = re.compile(r"""
    (\s+)?  # CAPTURE GROUP (1) | Match between 1 and ∞ whitespaces, as many
            # times as possible, as either one or zero matches.
    [-*+]+  # Match between 1 and ∞ "-", "*", or "+".
    \s+     # Match between 1 and ∞ whitespaces.
    (.+?)   # CAPTURE GROUP (2) | Match between 1 and ∞ characters, as few
            # times as possible.
    \s*     # Match between 0 and ∞ whitespaces.""", re.VERBOSE)

# Tags that do not need be enclosed in <p> tags:
INDEPENDENT_TAGS = (
    "<h",           # Headings and horizontal rules.
    "<a",           # Links.
    "<img",         # Images.
    "<code",        # Code.
    "<blockquote",  # Blockquotes.
    "<ol",          # Ordered lists.
    "<ul",          # Ordered lists.
)

NESTED_TAGS = (
    {
        "regex": REGEX_BLOCKQUOTE,
        "outer_opening_tag": "<blockquote>",
        "outer_closing_tag": "</blockquote>",
        "inner_opening_tag": "<p>",
        "inner_closing_tag": "</p>",
        "inner_ignore_tags": INDEPENDENT_TAGS,
        "minimum_level": 1
    },
    {
        "regex": REGEX_ORDERED_LIST,
        "outer_opening_tag": "<ol>",
        "outer_closing_tag": "</ol>",
        "inner_opening_tag": "<li>",
        "inner_closing_tag": "</li>",
        "inner_ignore_tags": None,
        "minimum_level": 0
    },
    {
        "regex": REGEX_UNORDERED_LIST,
        "outer_opening_tag": "<ul>",
        "outer_closing_tag": "</ul>",
        "inner_opening_tag": "<li>",
        "inner_closing_tag": "</li>",
        "inner_ignore_tags": None,
        "minimum_level": 0
    }
)


def is_paragraph(line):
    """
    Check if a line is a paragraph.

    Args:
        line (str): Line to check.

    Returns:
        bool: Whether or not the line is a paragraph.
    """
    line = line.strip()

    # A paragraph can start with a "<br>", but not just be a "<br>".
    return line not in ("", "<br>") and not line.startswith(INDEPENDENT_TAGS)


def convert_nested_tag(line, cur_tag, open_tags):
    """
    Convert one or more nested tags in a line.

    Conversion is based on the level of the last tag open, opening a new tag if
    the current level is greater than the last, and closing the last tag if the
    current level is lesser than the last.

    E.g.:
        > Quote Level 1
        Becomes:
        <blockquote>
            <p>Quote Level 1</p>

        > Quote Level 1
        >> Quote Level 2
        > Quote Level 1
        Becomes (after function runs on the three lines):
        <blockquote>
            <p>Quote Level 1</p>
            <blockquote>
                <p>Quote Level 2</p>
            </blockquote>
            <p>Quote Level 1</p>

        > Quote Level 1
        >> Quote Level 2
        >>> Quote Level 3
        >>>> Quote Level 4
        Becomes (after function runs on the four lines):
        <blockquote>
            <p>Quote Level 1</p>
            <blockquote>
                <p>Quote Level 2</p>
                <blockquote>
                    <p>Quote Level 3</p>
                    <blockquote>
                        <p>Quote Level 4</p>

    Args:
        line (str): Line to convert.
        cur_tag (dict[str, Any]): Dictionary containing data about type of tag
            used in conversion.
        open_tags (list[tuple[dict[str, Any], int]]): A list of tuples which
            represent tags left open, where each tuple contains a dictionary
            representing a tag, and its respective level.
    Returns:
        new_line (str) : Converted line.
    """
    def inner_tags(string, tag):
        """
        Add opening and closing inner tags to a string, if required.

        Inner tags will be added to string only if the string does not start
        with a tag ignored by this tag. For example, lists within blockquotes
        should not be surrounded by paragraph tags, so they are ignored.

        Args:
            string (str): String to add tags to.
            tag (tuple[dict[str, Any]]): A dictionary representing a tag.

        Returns:
            string: Resulting string.
        """
        ignored = tag["inner_ignore_tags"]
        if ignored and any(string.startswith(i) for i in ignored):
            return string
        return "".join((
            tag["inner_opening_tag"],
            string,
            tag["inner_closing_tag"]
        ))

    def convert_inline(string):
        """
        Recursively convert nested tags present in a string.

        This function should only be used to convert nested tags present in the
        content of another nested tag. That is, it is only useful for nested
        tags which are on the same line as an initially matched main tag, since
        it does not account for levels.

        E.g.:
            "1. - Unordered list inside an ordered list."
            Becomes:
            <ol>
                <li>
                    <ul>
                        <li>Unordered list inside an ordered list.</li>
                    </ul>
                </li>
            </ol>

        Args:
            string (str): String to convert.

        Returns:
            string: Converted string.
        """
        for tag in NESTED_TAGS:
            match = tag["regex"].fullmatch(string)
            if match:
                content = match[2]
                string = "".join((
                    tag["outer_opening_tag"],
                    inner_tags(convert_inline(content.strip()), tag),
                    tag["outer_closing_tag"]
                ))
        return string

    new_line = ""
    match = cur_tag["regex"].fullmatch(line)

    try:
        last_tag = open_tags[-1][0]
        last_tag_level = open_tags[-1][1]
    except IndexError:
        last_tag_level = 0
    try:
        # 1 is added to ensure level is never less than 1. This prevents
        # inconsistent behavior from arising due to lists minimum level being
        # zero, and blockquotes minimum level being 1. This mainly addresses
        # inconsistencies when tags are used separately.
        cur_tag_level = len(match[1]) + 1
    except TypeError:
        cur_tag_level = 1

    # Tag minimum level is removed from the current level due to the same
    # reason as above. This mainly addresses inconsistencies when tags are
    # mixed.
    cur_tag_level -= cur_tag["minimum_level"]

    content = convert_inline(match[2])

    # If current level is greater than last level, open a new tag, then append
    # tag and level to the list of open tags.
    if cur_tag_level > last_tag_level:
        new_line = "".join((
            cur_tag["outer_opening_tag"],
            inner_tags(content, cur_tag)
        ))
        open_tags.append((cur_tag, cur_tag_level))

    # If current level is lesser than last level:
    elif cur_tag_level < last_tag_level:
        # If none of the open tags have a level equal to or lesser than current
        # level, close the last tag, remove it from the list of open tags, open
        # a new tag, and add it to the list of open tags. This is checked
        # mainly to account for edge cases.
        if not any(open_tag[1] <= cur_tag_level for open_tag in open_tags):
            new_line = "".join((
                last_tag["outer_closing_tag"],
                cur_tag["outer_opening_tag"],
                inner_tags(content, cur_tag)
            ))
            open_tags.remove(open_tags[-1])
            open_tags.append((cur_tag, cur_tag_level))
        else:
            # Go through open tags, closing them until a tag's level is equal
            # to or lesser than current level.
            for open_tag in reversed(open_tags):
                tag, level = open_tag
                if level > cur_tag_level:
                    new_line += tag["outer_closing_tag"]
                    open_tags.remove(open_tag)
                else:
                    # If this tag is the same type as current tag, open inner
                    # tags only.
                    if tag == cur_tag:
                        new_line += inner_tags(content, cur_tag)

                    # If not, then close it, remove it from the list of open
                    # tags, open a new tag and add it to the list of open tags.
                    else:
                        new_line += "".join((
                            tag["outer_closing_tag"],
                            cur_tag["outer_opening_tag"],
                            inner_tags(content, cur_tag)
                        ))
                        open_tags.remove(open_tag)
                        open_tags.append((cur_tag, cur_tag_level))
                    break

    # If current level is the same as last level:
    else:
        # If last tag is the same type as current tag, open inner tags only.
        if last_tag == cur_tag:
            new_line = inner_tags(content, cur_tag)

        # If not, then close it, remove it from the list of open tags, open a
        # new tag, and add it to the list of open tags.
        else:
            new_line = "".join((
                last_tag["outer_closing_tag"],
                cur_tag["outer_opening_tag"],
                inner_tags(content, cur_tag)
            ))
            open_tags.remove(open_tags[-1])
            open_tags.append((cur_tag, cur_tag_level))

    return new_line


def convert(string):
    """
    Convert Markdown into HTML.

    Args:
        string (str): Markdown code to be converted.

    Returns:
        new_string (str): HTML code.
    """
    if string.strip() == "":
        return ""

    open_tags = []
    new_string = ""
    add_line_break = False
    open_paragraph = False

    def convert_paragraph(line):
        """
        Convert a line into a paragraph.

        Args:
            line (str): Line to convert.

        Returns:
            str: Converted line.
        """
        nonlocal open_paragraph
        if not open_paragraph:
            open_paragraph = True
            return f"<p>{line.lstrip()}"
        return line

    # Ensure string ends with a newline to prevents inconsistencies.
    while string.splitlines()[-1] != "":
        string += "\n"

    for line in string.splitlines():
        new_line = ""

        # Add horizontal rules.
        line = REGEX_HORIZONTAL_RULE.sub("<hr>", line)

        # Add emphasis.
        # The order here is important, otherwise "**bold**" would be converted
        # to "*<em>bold</em>*", instead of "<strong>bold</strong>".
        line = REGEX_BOLD.sub("<strong>\\1\\2</strong>", line)
        line = REGEX_ITALIC.sub("<em>\\1\\2</em>", line)

        # Add code.
        line = REGEX_CODE.sub("<code>\\1\\2</code>", line)

        # Add images and links.
        # The order here is important, otherwise images wouldn't work.
        if REGEX_IMAGE.search(line):
            match = REGEX_LINK.search(line)
            alt_text, url, title = match.groups()
            line = REGEX_IMAGE.sub(
                f'<img src="{url}" alt="{alt_text}"'
                + (f' title="{title}"' if title else '')
                + '>', line)
        if REGEX_LINK.search(line):
            match = REGEX_LINK.search(line)
            alt_text, url, title = match.groups()
            line = REGEX_LINK.sub(
                f'<a href="{url}"'
                + (f' title="{title}"' if title else '')
                + f'>{alt_text}</a>', line)

        # Add headings.
        if REGEX_HEADING.search(line):
            level = len(REGEX_HEADING.search(line)[2])
            line = REGEX_HEADING.sub(f"\\1<h{level}>\\3</h{level}>\\4", line)

        # Check if line contains nested tags, if so, open tags.
        if any(tag["regex"].fullmatch(line) for tag in NESTED_TAGS):
            for tag in NESTED_TAGS:
                if tag["regex"].fullmatch(line):
                    new_line = convert_nested_tag(line, tag, open_tags)

        # If not, check if there are open tags, if so, close them. After doing
        # so, check whether the line is a paragraph and add it accordingly.
        elif open_tags:
            for tag in reversed(open_tags):
                new_line += tag[0]["outer_closing_tag"]
                open_tags.remove(tag)
            if is_paragraph(line):
                new_line += convert_paragraph(line)
            else:
                new_line += line

        # If not, check if line is a paragraph, if so, open a paragraph.
        elif is_paragraph(line):
            new_line += convert_paragraph(line)

        # If not, just add the line as it is.
        else:
            new_line += line

        # Escape characters.
        if REGEX_ESCAPED_CHARACTER.search(new_line):
            new_line = REGEX_ESCAPED_CHARACTER.sub("\\1", new_line)

        # Add line breaks.
        if add_line_break:
            new_line = f"<br>{new_line}"
            add_line_break = False

        # Check if a line break should be added.
        if line.lstrip().endswith("  "):
            new_line = new_line.rstrip()
            add_line_break = True

        # Close paragraph.
        if open_paragraph and not is_paragraph(new_line):
            open_paragraph = False
            new_line = f"</p>{new_line}"

        new_string += new_line
    return new_string.strip()


def convert_file(file):
    """
    Open a Markdown file and return converted results.

    Args:
        file (TextIO): Markdown file to be converted.

    Returns:
        str: HTML code.
    """
    with open(file) as f:
        return convert(f.read())
