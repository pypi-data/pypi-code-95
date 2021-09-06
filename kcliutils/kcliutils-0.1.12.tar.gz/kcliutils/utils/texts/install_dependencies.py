# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import List

# Pip
from kdependencies import InstalledPackage

# Local
from .core_texts import install_dependencies

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def new_install_dependencies_file(packages: List[InstalledPackage]) -> str:
    return install_dependencies.replace(
        '[COMMANDS]',
        '\n'.join([p.get_install_command() for p in packages])
    )


# -------------------------------------------------------------------------------------------------------------------------------- #