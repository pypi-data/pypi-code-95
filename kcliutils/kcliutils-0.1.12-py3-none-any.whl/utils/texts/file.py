# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# Local
from .core_texts import file
from .utils import multi_replace
from .all_file_consts import AllFileConsts

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def new_file(
    tab_size: int,
    comment_line_len: int,
) -> str:
    return multi_replace(
        file,
        tab_size=tab_size,
        comment_line_len=comment_line_len,
        file_consts=AllFileConsts.PY.value
    )


# -------------------------------------------------------------------------------------------------------------------------------- #