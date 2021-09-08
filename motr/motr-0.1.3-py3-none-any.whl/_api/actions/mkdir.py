import pathlib
import typing

import attr
import trio

import motr._api.actions.io
import motr._api.requirements.action
import motr._api.requirements.requirements
import motr._api.requirements.target
import motr.core.result


@attr.dataclass(frozen=True)
class Mkdir:
    path: pathlib.Path

    async def __call__(
        self,
    ) -> typing.Tuple[motr.core.result.Result, typing.Mapping[str, str]]:
        try:
            await trio.Path(self.path).mkdir(parents=True, exist_ok=True)
        except Exception:
            return motr.core.result.Result.ABORTED, {}
        return motr.core.result.Result.PASSED, {}


def mkdir(
    path: motr._api.actions.io.Input,
) -> motr._api.requirements.requirements.Requirements:
    action = Mkdir(path.path)
    yield from motr._api.requirements.action.action(action)
    yield from motr._api.requirements.target.target(path.path, action)
