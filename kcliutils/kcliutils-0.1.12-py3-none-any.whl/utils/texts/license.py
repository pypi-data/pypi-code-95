# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from datetime import datetime

# Local
from .core_texts import license
from .utils import multi_replace
from .file_key import FileKey
from .all_file_consts import AllFileConsts

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def new_license(author_name: str) -> str:
    return multi_replace(
        license,
        keys_vals={
            FileKey.YEAR: datetime.utcnow().year,
            FileKey.AUTHOR_NAME: author_name
        },
        file_consts=AllFileConsts.PY.value
    )

# -------------------------------------------------------------------------------------------------------------------------------- #