from __future__ import annotations

import functools
import typing

import attr
import pyrsistent

if typing.TYPE_CHECKING:
    import motr.core.runner
    import motr.core.target
    import motr.core.target_name


@attr.dataclass(frozen=True)
class Action:
    action: motr.core.runner.RuntimeAction


@attr.dataclass(frozen=True)
class ActionInput:
    action: motr.core.runner.RuntimeAction
    target: motr.core.target.Target


@attr.dataclass(frozen=True)
class ActionOutput:
    parent: motr.core.runner.RuntimeAction
    target: motr.core.target.Target


@attr.dataclass(frozen=True)
class TargetName:
    target: motr.core.target.Target
    name: motr.core.target_name.TargetName


@attr.dataclass(frozen=True)
class SkippedName:
    name: motr.core.target_name.TargetName


Requirement = typing.Union[
    Action, ActionInput, ActionOutput, TargetName, SkippedName
]


@attr.dataclass(frozen=True)
class ActionData:
    inputs: pyrsistent.PSet[motr.core.target.Target] = pyrsistent.pset()

    def add_input(self, target: motr.core.target.Target) -> ActionData:
        return attr.evolve(self, inputs=self.inputs.add(target))


@attr.dataclass(frozen=True)
class Registry:
    # These are the user-selectable targets.
    # A single name can refer to multiple targets.
    _choosable_targets: pyrsistent.PMap[
        motr.core.target_name.TargetName,
        pyrsistent.PSet[motr.core.target.Target],
    ] = pyrsistent.pmap()
    # These are the defined actions.
    _actions: pyrsistent.PMap[
        motr.core.runner.RuntimeAction, ActionData
    ] = pyrsistent.pmap()
    # This is the mapping from targets to prerequisites.
    # A single action can satisfy many targets.
    _parent_action: pyrsistent.PMap[
        motr.core.target.Target, motr.core.runner.RuntimeAction
    ] = pyrsistent.pmap()
    # Some user-selectable targets are not selected by default.
    # That is indicated with this set.
    _default_skips: pyrsistent.PSet[
        motr.core.target_name.TargetName
    ] = pyrsistent.pset()
    _last_added: typing.Optional[motr.core.runner.RuntimeAction] = None

    def inputs(
        self, action: motr.core.runner.RuntimeAction
    ) -> pyrsistent.PSet[motr.core.target.Target]:
        return self._actions[action].inputs

    def chosen_targets(
        self, names: typing.Iterable[motr.core.target_name.TargetName]
    ) -> typing.Set[motr.core.target.Target]:
        return {
            target
            for name in names
            for target in self._choosable_targets[name]
        }

    def parent(
        self, target: motr.core.target.Target
    ) -> motr.core.runner.RuntimeAction:
        return self._parent_action[target]

    def default_and_non_default(
        self,
    ) -> typing.Tuple[
        typing.List[motr.core.target_name.TargetName],
        typing.List[motr.core.target_name.TargetName],
    ]:
        return (
            sorted(
                set(self._choosable_targets).difference(self._default_skips)
            ),
            sorted(self._default_skips),
        )

    def _require_action(self, requirement: Action) -> Registry:
        if requirement.action in self._actions:
            return self
        return attr.evolve(
            self,
            actions=self._actions.set(requirement.action, ActionData()),
            last_added=requirement.action,
        )

    def _require_action_input(self, requirement: ActionInput) -> Registry:
        if requirement.action not in self._actions:
            raise ValueError(
                f"Cannot add target {requirement.target!r} as an input to"
                f" action {requirement.action!r}. Action"
                f" {requirement.action!r} has not been added to the registry."
            )
        if requirement.target not in self._parent_action:
            raise ValueError(
                f"Cannot add target {requirement.target!r} as an input to"
                f" action {requirement.action!r}. Target"
                f" {requirement.target!r} has not been added to the registry."
            )
        if self._parent_action[requirement.target] == requirement.action:
            raise ValueError(
                f"Cannot add target {requirement.target!r} as an input to"
                f" action {requirement.action!r}. The parent action of target"
                f" {requirement.target!r} is {requirement.action!r}."
            )
        if requirement.target in self._actions[requirement.action].inputs:
            return self
        if requirement.action != self._last_added:
            raise ValueError(
                f"Cannot add target {requirement.target!r} as an input to"
                f" action {requirement.action!r}. The most recently added"
                f" action is {self._last_added!r}."
            )
        return attr.evolve(
            self,
            actions=self._actions.set(
                requirement.action,
                self._actions[requirement.action].add_input(
                    requirement.target
                ),
            ),
        )

    def _require_action_output(self, requirement: ActionOutput) -> Registry:
        if (
            self._parent_action.get(requirement.target, requirement.parent)
            != requirement.parent
        ):
            raise ValueError(
                f"Cannot add target {requirement.target!r} with parent action"
                f" {requirement.parent!r}."
                f" Target {requirement.target!r} already has parent action"
                f" {self._parent_action[requirement.target]!r}."
            )
        if requirement.parent not in self._actions:
            raise ValueError(
                f"Cannot add target {requirement.target!r} with parent action"
                f" {requirement.parent!r}."
                f" Parent action {requirement.parent!r} has not been added to"
                " the registry."
            )
        return attr.evolve(
            self,
            parent_action=self._parent_action.set(
                requirement.target, requirement.parent
            ),
        )

    def _require_target_name(self, requirement: TargetName) -> Registry:
        if requirement.target not in self._parent_action:
            raise ValueError(
                f"Cannot name target {requirement.target!r}"
                f" {requirement.name!r}."
                f" Target {requirement.target!r} has not been added to the"
                " registry."
            )
        return attr.evolve(
            self,
            choosable_targets=self._choosable_targets.set(
                requirement.name,
                self._choosable_targets.get(
                    requirement.name, pyrsistent.pset()
                ).add(requirement.target),
            ),
        )

    def _require_skipped_name(self, requirement: SkippedName) -> Registry:
        if requirement.name not in self._choosable_targets:
            raise ValueError(
                f"Cannot skip name {requirement.name!r}."
                f" Name {requirement.name!r} has not been assigned to any"
                " target."
            )
        return attr.evolve(
            self, default_skips=self._default_skips.add(requirement.name)
        )

    def require(self, requirement: Requirement) -> Registry:
        raise NotImplementedError

    if not typing.TYPE_CHECKING:  # pragma: no branch
        require = functools.singledispatchmethod(require)
        # We need to specify the exact classes, because relying on annotations
        # doesn't work.
        # This is because it resolves the *entire* annotation, even though it
        # arguably doesn't need it, and it can't resolve the return value,
        # because the class isn't bound to the module namespace yet.
        require.register(Action, _require_action)
        require.register(ActionInput, _require_action_input)
        require.register(ActionOutput, _require_action_output)
        require.register(TargetName, _require_target_name)
        require.register(SkippedName, _require_skipped_name)
