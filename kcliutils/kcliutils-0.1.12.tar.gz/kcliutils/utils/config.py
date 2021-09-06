# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
import inspect

# Pip
from jsoncodable import JSONCodable

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Config -------------------------------------------------------- #

class Config(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        default_author: str,
        default_commit_message: str,
        default_min_python_version: float,
        default_max_python_version: float,
        spaces_per_tab: int,
        comment_line_length: int
    ):
        self.default_author = default_author
        self.default_commit_message = default_commit_message
        self.default_min_python_version = default_min_python_version
        self.default_max_python_version = default_max_python_version
        self.spaces_per_tab = spaces_per_tab
        self.comment_line_length = comment_line_length


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def validate(self) -> None:
        for attr in inspect.getfullargspec(self.__init__).args[1:]:
            getattr(self, attr)


# -------------------------------------------------------------------------------------------------------------------------------- #