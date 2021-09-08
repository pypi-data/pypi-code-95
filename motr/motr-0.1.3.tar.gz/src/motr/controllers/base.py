import contextlib
import pathlib
import traceback
import typing
from os import chdir  # Allow for easier monkey-patching in testing.

import attr
import tqdm
import trio
from cement import Controller
from cement.utils.version import get_version_banner

import motr
import motr.core.exc
import motr.core.registry
import motr.core.result
import motr.core.runner
import motr.core.target_name

VERSION_BANNER = """
An Opinionated Task Runner %s
%s
""" % (
    motr.__version__,
    get_version_banner(),
)

MOTRFILE_NAME = "motrfile.py"

ResultList = typing.List[
    typing.Tuple[motr.core.runner.RuntimeAction, typing.Mapping[str, str]]
]


@attr.dataclass(frozen=True)
class TQDM:
    pbar: tqdm.tqdm

    @contextlib.contextmanager
    def __call__(
        self,
        action: motr.core.runner.RuntimeAction,
    ) -> typing.Iterator[None]:
        self.pbar.total += 1
        self.pbar.update(0)
        # Do not wrap, because we *want* to skip "cleanup" on failure.
        yield
        self.pbar.update()


def path_from_arg() -> pathlib.Path:
    cwd_path = pathlib.Path(MOTRFILE_NAME).resolve()
    if cwd_path.exists():
        return cwd_path
    for pwd in pathlib.Path(".").resolve().parents:
        motrfile = pwd / MOTRFILE_NAME
        if motrfile.exists():
            return motrfile
    return cwd_path


def motr_open(motrfile: pathlib.Path) -> typing.BinaryIO:
    try:
        return open(motrfile, mode="rb")
    except FileNotFoundError:
        raise motr.core.exc.MOTRError(f"MOTRfile {motrfile} not found.")
    except IsADirectoryError:
        raise motr.core.exc.MOTRError(
            f"MOTRfile at {motrfile} is a directory."
        )
    except PermissionError:
        raise motr.core.exc.MOTRError(
            f"Insufficient permissions to read MOTRfile at {motrfile}."
        )
    except OSError:
        raise motr.core.exc.MOTRError(
            f"Unexpected IO error reading MOTRfile at {motrfile}."
            " Please file an issue."
        )
    except Exception:
        raise motr.core.exc.MOTRError(
            f"Unexpected general error reading MOTRfile at {motrfile}."
            " Please file an issue."
        )


class Base(Controller):
    class Meta:
        label = "base"

        # text displayed at the top of --help output
        description = "An Opinionated Task Runner"

        # text displayed at the bottom of --help output
        epilog = "Usage: motr"

        # controller level arguments. ex: 'motr --version'
        arguments = [
            # add a version banner
            (
                ["-v", "--version"],
                {"action": "version", "version": VERSION_BANNER},
            ),
            (["-l", "--list-targets", "--list"], {"action": "store_true"}),
            (
                ["-t", "--target", "-s", "-e"],
                {"action": "append", "type": motr.core.target_name.TargetName},
            ),
        ]

    def _default(self) -> None:
        """Default action if no sub-command is passed."""

        motrfile = path_from_arg()
        # Hardcode the path for now
        motrdir = motrfile.parent
        chdir(motrdir)
        with motr_open(motrfile) as fh:
            motrfile_text = fh.read()
        try:
            compiled_code = compile(motrfile_text, motrfile, "exec")
        except (SyntaxError, ValueError):
            raise motr.core.exc.MOTRError(
                f"Could not parse MOTRfile at {motrfile};"
                " encountered the following exception:"
                f"\n{traceback.format_exc()}"
            )
        motr_globals: typing.Dict[str, typing.Any] = {}
        try:
            exec(compiled_code, motr_globals)
        except Exception:
            raise motr.core.exc.MOTRError(
                f"The MOTRfile at {motrfile}"
                " encountered the following exception:"
                f"\n{traceback.format_exc()}"
            )
        if "MOTR_CONFIG" not in motr_globals:
            raise motr.core.exc.MOTRError(
                f"The MOTRfile at {motrfile}"
                " did not produce a configuration object."
            )
        motr_config = motr_globals["MOTR_CONFIG"]
        if not isinstance(motr_config, motr.core.registry.Registry):
            raise motr.core.exc.MOTRError(
                f"The MOTRfile at {motrfile} produced an invalid "
                f"configuration object: {motr_config}"
            )
        default, non_default = motr_config.default_and_non_default()
        if self.app.pargs.list_targets:
            self.app.render(
                {"default": default, "non_default": non_default}, "list.jinja2"
            )
            return
        target_names = default
        if self.app.pargs.target is not None:
            target_names = self.app.pargs.target
        targets = motr_config.chosen_targets(target_names)
        passed: ResultList = []
        failed: ResultList = []
        aborted: ResultList = []
        results: typing.Dict[motr.core.result.Result, ResultList] = {
            motr.core.result.Result.PASSED: passed,
            motr.core.result.Result.FAILED: failed,
            motr.core.result.Result.ABORTED: aborted,
        }
        with tqdm.tqdm(total=0) as pbar:
            target_runner = motr.core.runner.Target(
                motr_config, TQDM(pbar), results
            )
            trio.run(motr.core.runner.run_all, target_runner, targets)
        self.app.render(
            {
                "passed": sorted([str(item[0]) for item in passed]),
                "failed": sorted([str(item[0]) for item in failed]),
                "aborted": sorted([str(item[0]) for item in aborted]),
            },
            "results.jinja2",
        )
