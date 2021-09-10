import os
import os.path as op

from termcolor import cprint

from .config import LAMPIP_CONFIG_TOML_TEMPLATE, Config, validate_layername
from .package import deploy_package


class Workspace:
    def __init__(self, directory: str, layername: str):
        self.directory = directory
        self.layername = layername

    @classmethod
    def create_scaffold(cls, layername) -> "Workspace":
        """Create the scaffold to the specified directory

        Files
        - requirements.txt: empty file
        - lampip-config.toml
        - other_layer_resources/bin
        - other_layer_resources/lib
        - other_layer_resources/python

        """
        validate_layername(layername)
        directory = op.join(".", layername)
        if op.exists(directory):
            raise FileExistsError(f"{directory} already exists")
        cprint(f"Create the scaffold: {layername}", color="green")
        os.mkdir(directory)
        # requirements.txt: empty file
        with open(op.join(directory, "requirements.txt"), "wt") as fp:
            pass
        # lampip-config.toml
        with open(op.join(directory, "lampip-config.toml"), "wt") as fp:
            fp.write(LAMPIP_CONFIG_TOML_TEMPLATE.substitute(layername=layername))
        # other_resources/bin
        # other_resources/lib
        # other_resources/python
        os.makedirs(op.join(directory, "other_resources", "bin"))
        os.makedirs(op.join(directory, "other_resources", "lib"))
        os.makedirs(op.join(directory, "other_resources", "python"))

        print(
            f"+ {op.join(directory, 'requirements.txt')}\n"
            f"+ {op.join(directory, 'lampip-confing.toml')}\n"
            f"+ {op.join(directory, 'other_resources', 'bin')}\n"
            f"+ {op.join(directory, 'other_resources', 'lib')}\n"
            f"+ {op.join(directory, 'other_resources', 'python')}"
        )

        return cls(directory, layername)

    @classmethod
    def load_directory(cls, directory: str) -> "Workspace":
        os.chdir(directory)
        config = Config.load_toml(op.join(directory, "lampip-config.toml"))
        return cls(directory, config.layername)

    def deploy(self, upload_also=True):
        """Build and upload the lambda custom layer."""
        config = Config.load_toml(op.join(self.directory, "lampip-config.toml"))
        deploy_package(config, upload_also)
