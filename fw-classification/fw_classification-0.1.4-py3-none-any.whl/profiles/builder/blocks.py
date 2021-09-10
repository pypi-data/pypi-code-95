"""Module to help with building blocks."""
import logging
import typing as t

from fw_classification.classify.block import Block, Evaluate
from fw_classification.classify.expressions import Regex, Set, expression_map
from fw_classification.classify.rule import Action, Match, Rule

log = logging.getLogger(__name__)


def block_from_context_classifications(
    classifications: t.Dict[str, t.Dict[str, str]]
) -> t.Optional[Block]:
    """Build a block from a list of context classifications.

    Converts context classifications from dictionaries (see format below)
    to a block that is appended to the profile.

    Dictionary:

    .. code-block ::python

        {<field> :
            <criteria> : <action>
            ...
        }

    Where ``<criteria>`` can either be an operator, or a regex between two `/`
    marks.
    """
    if not isinstance(classifications, dict):
        log.warning(f"Classifications must be an object, found {classifications}")
        return None
    rules: t.List[Rule] = []
    for field, rule in classifications.items():
        if not isinstance(field, str):
            log.warning(f'Classification keys must be string, found: "{field}"')
            continue
        if not isinstance(rule, dict):
            log.warning(f'Classification values must be an object, found: "{rule}"')
            continue
        for match, action in rule.items():
            if not isinstance(match, str):
                log.warning(f'Match criteria must be string, found: "{match}"')
                continue
            if not isinstance(action, str):
                log.warning(f'Action criteria must be string, found: "{action}"')
                continue
            match_obj = parse_match_from_string(field, match)
            action_obj = parse_action_from_string(action)
            if not (match_obj and action_obj):
                log.warning("Both match and action must be present")
                continue
            rule_obj = Rule(match_obj, action_obj)
            rules.append(rule_obj)
    if rules:
        block = Block(
            "Custom classification",
            rules,
            eval_type=Evaluate.All,
            description="Custom classification block",
        )
        return block
    return None


def parse_action_from_string(action_str: str) -> t.Optional[Action]:
    """Parse an action object from a string."""
    actions = action_str.split(",")
    parsed_actions: t.List[Set] = []
    for action in actions:
        try:
            field, value = action.split(":")
            field = field.strip(" ")
            value = value.strip(" ")
            parsed_actions.append(Set(field, value))
        except ValueError:
            log.warning(f"Could not parse action {action}")
            return None
    return Action(parsed_actions)  # type: ignore


def parse_match_from_string(field: str, match_str: str) -> t.Optional[Match]:
    """Parse a match object from a string."""
    if len(match_str) > 2 and match_str[0] == "/" and match_str[-1] == "/":
        # Regex rule
        return Match([Regex(field, match_str[1:-1])])
    try:
        key, val = match_str.split(":")
        key = key.strip(" ").lower()
        val = val.strip(" ")
        _, Op = expression_map[key]
        match_obj = Match([Op(field, val)])
        return match_obj
    except (KeyError, ValueError):
        log.warning(f'Could not parse match criteria "{match_str}"')
        return None
