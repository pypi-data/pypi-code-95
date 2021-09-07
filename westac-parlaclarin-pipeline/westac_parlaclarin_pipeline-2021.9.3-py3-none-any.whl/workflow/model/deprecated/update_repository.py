import os
from glob import glob

from snakemake import shell
from workflow.model.utility.utils import strip_paths


def update_repository(config: dict) -> None:

    repository_folder = config.get('parla_clarin', {}).get('repository_folder')
    repository_data_folder = config.get('parla_clarin', {}).get('folder')
    speech_xml_folder = config.get('transformed_speeches', {}).get('folder')

    print("Updating Para-Clarin XML repository")

    if not os.path.isdir(repository_folder):
        raise FileNotFoundError(repository_folder)

    cwd = os.getcwd()
    os.chdir(repository_folder)

    shell("git fetch --depth 1 && git reset --hard origin && git clean -dfx")

    for target_path in glob(os.path.join(speech_xml_folder, "*.xml")):
        basename = strip_paths(target_path)
        source_path = os.path.join(repository_data_folder, basename)

        if not os.path.isfile(source_path):
            os.remove(target_path)
            shell(f"zip -qdo gallery.zip {basename} ")

    os.chdir(cwd)
