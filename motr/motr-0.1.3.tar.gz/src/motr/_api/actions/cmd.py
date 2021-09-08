from __future__ import annotations

import pathlib
import types
import typing

import attr
import pyrsistent
import trio

import motr._api.actions.io
import motr._api.requirements.action
import motr._api.requirements.requirements
import motr._api.requirements.target
import motr.core.result
import motr.core.target

CmdArg = typing.Union[motr._api.actions.io.IOType, str]


@attr.dataclass(frozen=True)
class Cmd:
    cmd: typing.Tuple[str, ...]
    env: pyrsistent.PMap[str, str] = pyrsistent.pmap()
    allowed_codes: pyrsistent.PSet[int] = pyrsistent.pset()

    async def __call__(
        self,
    ) -> typing.Tuple[motr.core.result.Result, typing.Mapping[str, str]]:
        cmd_result = await trio.run_process(
            self.cmd,
            capture_stdout=True,
            capture_stderr=True,
            check=False,
            env=dict(self.env),
        )
        returncode = cmd_result.returncode
        failed = bool(returncode)
        return motr.core.result.Result(
            (failed, failed and returncode not in self.allowed_codes)
        ), {
            "out": cmd_result.stdout.decode(),
            "err": cmd_result.stderr.decode(),
        }


def cmd_(
    cmd: typing.Sequence[CmdArg],
    *inputs: motr.core.target.CoerceToTarget,
    allowed_codes: typing.Collection[int] = frozenset(),
    env: typing.Mapping[str, CmdArg] = types.MappingProxyType({})
) -> motr._api.requirements.requirements.Requirements:
    action = Cmd(
        tuple(
            str(arg.path) if isinstance(arg, motr._api.actions.io.IO) else arg
            for arg in cmd
        ),
        allowed_codes=pyrsistent.pset(allowed_codes),
        env=pyrsistent.pmap(
            {
                key: str(val.path)
                if isinstance(val, motr._api.actions.io.IO)
                else val
                for key, val in env.items()
            }
        ),
    )
    yield from motr._api.requirements.action.action(
        action, *inputs, *extra_inputs(cmd), *extra_inputs(env.values())
    )
    yield from extra_targets(action, cmd)
    yield from extra_targets(action, env.values())
    return action


def extra_inputs(
    cmd_args: typing.Iterable[CmdArg],
) -> typing.Iterator[pathlib.Path]:
    for cmd_arg in cmd_args:
        if isinstance(cmd_arg, motr._api.actions.io.Input):
            yield cmd_arg.path


def extra_targets(
    action: motr.core.runner.RuntimeAction,
    cmd_args: typing.Iterable[CmdArg],
) -> motr._api.requirements.requirements.Requirements:
    for cmd_arg in cmd_args:
        if isinstance(cmd_arg, motr._api.actions.io.Output):
            yield from motr._api.requirements.target.target(
                cmd_arg.path, action, *cmd_arg.names
            )
