# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------- class: FileConsts ------------------------------------------------------ #

class FileConsts:

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        file_extension: str,
        comment_starter: str,
        comment_line_char: Optional[str] = None
    ):
        self.file_extension = file_extension
        self.comment_starter = comment_starter

        self.comment_line_char = comment_line_char


    # --------------------------------------------------- Public properties -------------------------------------------------- #

    @property
    def comment_ender(self) -> str:
        return self.comment_starter[::-1]


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def is_kind(self, path) -> bool:
        return path.lower().endswith(self.file_extension.lower())

    def is_comment_line(
        self,
        comment_line: str,
        comment_line_char: Optional[str] = None
    ) -> bool:
        comment_line_char = comment_line_char or self.comment_line_char

        if not comment_line_char:
            raise 'no comment line char specified'

        comment_line = comment_line.strip()
        comment_prefix = '{} {}'.format(self.comment_starter, comment_line_char)

        return comment_line.startswith(comment_prefix) and comment_line.endswith(comment_prefix[::-1])


    # -------------------------------------------------- Private properties -------------------------------------------------- #




    # ---------------------------------------------------- Private methods --------------------------------------------------- #




# -------------------------------------------------------------------------------------------------------------------------------- #