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
class WriteBytes:
    path: pathlib.Path
    data: bytes  # Put the responsibility for encoding on the caller.

    async def __call__(
        self,
    ) -> typing.Tuple[motr.core.result.Result, typing.Mapping[str, str]]:
        try:
            await trio.Path(self.path).write_bytes(self.data)
        except Exception:
            # Sure would be nice to put traceback information somewhere.
            return motr.core.result.Result.ABORTED, {}
        return motr.core.result.Result.PASSED, {}


def write_bytes(
    path: motr._api.actions.io.Input, data: bytes
) -> motr._api.requirements.requirements.Requirements:
    action = WriteBytes(path.path, data)
    yield from motr._api.requirements.action.action(action)
    yield from motr._api.requirements.target.target(path.path, action)
