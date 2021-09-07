"""Utilities for building profiles."""
import typing as t

from ruamel.yaml import YAML

from fw_classification.classify.expressions import Add, Regex
from fw_classification.classify.rule import Action, Match, MatchType, Rule

y = YAML(typ="safe")


def search_label_list_of_regex_rule(
    key: str, regexs: t.List[t.Tuple[str, str]], add_key: str, variables: t.Dict
) -> t.List[Rule]:
    """Create a list of rules with the following format.

    For a list of parameters key, (regex, add_value), add_key:
        make a list of:

    - match_type: any
      match:
        - key: {{ key }}
          regex: {{ regex }}
      action:
        - key: {{ add_key }}
          add: {{ add_value }}

    """
    rules: t.List[Rule] = []
    for reg, add_value in regexs:
        match_expr = Regex(key, reg)
        match = Match([match_expr], MatchType.Any, variables=variables)
        add_expr = Add(add_key, add_value)
        action = Action([add_expr], variables=variables)
        rule = Rule(match, action, MatchType.Any)
        rules.append(rule)

    #    y.dump(rules, stream=sys.stdout)
    return rules


def label_matches_list_of_regex(  # pylint: disable=unused-argument
    key: str, regexs: t.List[str], action: Action
) -> Rule:
    """Create a list of expressions for the match section of a rule."""


def compile_regex(string):
    """Generate the regex for label checking."""
    # Escape * for T2*
    if string == "T2*":
        string = r"T2\*"
        regex = r"(\b%s\b)|(_%s_)|(_%s)|(%s_)|(%s)|(t2star)" % (
            string,
            string,
            string,
            string,
            string,
        )
    # Prevent T2 from capturing T2*
    elif string == "T2":
        string = r"(?!T2\*)T2"
        regex = r"(\b%s\b)|(_%s_)|(_%s)|(%s_)" % (string, string, string, string)
    else:
        regex = r"(\b%s\b)|(_%s_)|(_%s)|(%s_)" % (string, string, string, string)
    return regex
