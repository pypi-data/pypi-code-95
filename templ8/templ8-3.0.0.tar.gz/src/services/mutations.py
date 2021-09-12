import logging
import os
import shutil
from pathlib import Path
from typing import List

from ..models.collection import Collection
from ..models.initialization import Initialization
from ..models.inputs import Inputs
from ..models.settings import Settings
from ..services.finders import select_files, select_top_level
from ..services.logging import log_process
from ..services.runtime import finalize_path, finalize_render_context
from ..services.templates import parse_template
from ..utils.strings.formatters import dry_run
from ..utils.strings.paths import (path_ext, path_tail, remove_ext,
                                   reverse_to_root)

logger = logging.getLogger(__file__)


def generate_collections(inputs: Inputs, collections: List[Collection]) -> None:
    if inputs.settings.clear_top_level:
        for path in select_top_level(inputs.settings):
            if inputs.flags.dry_run:
                logger.info(dry_run("Would remove file: %s"), path)

            else:
                logger.info("Removing file: %s", path, extra={"progress": True})
                os.remove(path)

    for collection in collections:
        for path in select_files(collection, inputs.settings):
            if inputs.flags.dry_run:
                logger.info(dry_run("Would generate file: %s"), path)

            else:
                logger.info("Generating file: %s", path, extra={"progress": True})
                generate_file(collection, inputs.settings, path)

        for initialization in collection.initializations:
            if inputs.flags.dry_run:
                logger.info(dry_run("Would run initialization: %s"), initialization.cmd)

            else:
                run_initialization(initialization, collection, inputs.settings)


def generate_file(collection: Collection, settings: Settings, path: str) -> None:
    target = os.path.join(
        settings.output,
        finalize_path(
            reverse_to_root(path, path_tail(collection.root)), collection, settings
        ),
    )

    if path_ext(target) == ".j2":
        target = remove_ext(target)
        Path(path_tail(target)).mkdir(parents=True, exist_ok=True)

        with open(target, "w", encoding="utf8") as stream:
            stream.write(
                parse_template(
                    path,
                    settings.loader_paths,
                    finalize_render_context(collection, settings),
                )
            )

    else:
        Path(path_tail(target)).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def run_initialization(
    initialization: Initialization, collection: Collection, settings: Settings
) -> None:
    cwd = os.path.normpath(
        os.path.join(
            settings.output, finalize_path(initialization.cwd, collection, settings)
        )
    )

    Path(cwd).mkdir(parents=True, exist_ok=True)
    log_process(logger, initialization.cmd.split(" "), cwd)
