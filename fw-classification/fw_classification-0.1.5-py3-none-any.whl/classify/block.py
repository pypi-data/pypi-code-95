"""Block module."""
import enum
import textwrap
import typing as t

from dotty_dict import Dotty

from .rule import Rule
from .utils import BlockError, ProfileError, configure_logging

log = configure_logging(__name__)


class Evaluate(str, enum.Enum):
    """Enum representing evaluate choices."""

    First: str = "first"
    All: str = "all"


class Block:  # pylint: disable=too-many-instance-attributes
    """Class to handle execution of a block in the profile."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        rules: t.List[Rule],
        eval_type: Evaluate = Evaluate.First,
        depends_on: t.Optional[t.List[str]] = None,
        variables: t.Optional[t.Dict[str, t.Union[t.Dict, str]]] = None,
        description: str = "",
    ) -> None:
        """Initialize a block.

        Args:
            name (str): Block name
            rules (List[Rule]): List of rules.
            eval_type (Evaluate, optional): Evaluation type, either "first" or "all".
                Defaults to Evaluate.First.
            depends_on (Optional[List[str]], optional): List of block names
                that should have run for this block to run.  Defaults to None.
            variables (Optional[Dict[str, str|Dict]], optional): Variable dictionary.
                Defaults to None.
            description (str): Description of block. Defaults to ''.
        """
        self.name = name
        self.description = description
        self.rules = rules
        self.eval_type = eval_type
        if not depends_on:
            self.depends_on = []
        else:
            self.depends_on = depends_on
        self.num_variable_vals = 1
        if variables:
            # True if any variable is multi-valued
            max_nums = 1
            for _, v in variables.items():
                num_keys = 1
                if isinstance(v, dict):
                    num_keys = len(v.keys())
                elif isinstance(v, list):
                    num_keys = len(v)
                if num_keys > max_nums:
                    max_nums = num_keys
            self.num_variable_vals = max_nums
            self.orig_variables = variables.copy()
        self.variables = self.gen_variables(variables)
        self._counter = 0

    @staticmethod
    def validate_variables(
        block_name: str, variables: t.Optional[t.Dict]
    ) -> t.Optional[ProfileError]:
        """Validate variables passed in.

        Must start with 0, and be monotonically increasing if dict.
        """
        if not variables:
            return None
        if not isinstance(variables, dict):
            return BlockError(
                block_name, f"Variables must be a mapping, found {variables}"
            )
        for _, value in variables.items():
            if isinstance(value, dict):
                counter = 0
                for index, _ in value.items():
                    if index != counter:
                        return BlockError(
                            block_name,
                            (
                                f"Variable index {index} is invalid.  Values "
                                "must start at 0 and monotonically increase."
                            ),
                        )
                    counter += 1
        return None

    def gen_variables(
        self, variables: t.Optional[t.Dict]
    ) -> t.Sequence[t.Optional[t.Dict]]:
        """Generate a list of variable dictionaries if multi-valued."""
        if not variables:
            return [
                None,
            ]
        variable_map: t.Sequence[dict] = [{} for _ in range(self.num_variable_vals)]
        for key, val in variables.items():
            if isinstance(val, dict):
                for i in range(self.num_variable_vals):
                    variable_map[i][key] = val[i]
            elif isinstance(val, list):
                for i in range(self.num_variable_vals):
                    variable_map[i][key] = val[i]
            else:
                for i in range(self.num_variable_vals):
                    variable_map[i][key] = val
        return variable_map

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate a rule block.

        Args:
            i_dict (Dotty): Input dictionary

        Returns:
            bool: Whether or not the block executed.
        """
        # Build result
        res = False
        while self._counter < self.num_variable_vals:
            for i, rule in enumerate(self.rules):
                rule.variables = self.variables[self._counter]
                out = rule.evaluate(i_dict)
                log.debug(f"Evaluated {self.name} rule #{i}, result: {out}")
                if out:
                    # If we're evaluating all, return True if one rule succeeded.
                    res = True
                    # If we're evaluating only the first, break out.
                    if self.eval_type == Evaluate.First:
                        break
            self._counter += 1
        log.info(f"Block {self.name} result: {res}")
        return res

    def __repr__(self) -> str:
        """String representation."""
        obj_repr = (
            "\nIf all of ("
            + ", ".join(self.depends_on)
            + ") executed, then execute "
            + ("the first match" if self.eval_type == Evaluate.First else "all of")
            + " of the following:\n\n"
        )
        for i, rule in enumerate(self.rules):
            obj_repr += f"\t{'-'*20} Rule {i} {'-'*20}\n"
            obj_repr += textwrap.indent(repr(rule), "\t", lambda l: True) + "\n\n"

        return obj_repr

    @classmethod
    def from_dict(  # pylint: disable=too-many-locals
        cls, block: t.Dict
    ) -> t.Tuple[t.Optional["Block"], t.List[ProfileError]]:
        """Instantiate a Block from a dictionary.

        Args:
            block (t.Dict): Block in dictionary form.

        Returns:
            Tuple:
                - Block or None
                - list of errors or []
        """
        errors: t.List[ProfileError] = []
        block_obj = None
        # Get name
        name = block.get("name", "")
        if not name:
            errors.append(BlockError(None, "Name must be specified."))
        # Get variables
        variables = block.get("variables")
        err = Block.validate_variables(name, variables)  # type: ignore
        if err:
            errors.append(err)
        # Get rules
        rules: t.List[Rule] = []
        raw_rules = block.get("rules", [])
        r_errs: t.List[ProfileError] = []
        for raw_rule in raw_rules:
            if raw_rule is None:
                continue
            errs: t.List[ProfileError] = []
            rule, errs = Rule.from_dict(raw_rule)
            if rule:
                rules.append(rule)
            r_errs.extend([e.add_component(f"block ({name})") for e in errs])
        errors.extend(r_errs)
        if not rules:
            if not r_errs:
                errors.append(
                    BlockError(
                        block.get("name", ""), "At least one rule must be specified."
                    )
                )
        # Get evaluation type
        raw_eval_type = block.get("evaluate", "first")
        eval_type = Evaluate.First
        if raw_eval_type == Evaluate.All.value:
            eval_type = Evaluate.All
        elif raw_eval_type == Evaluate.First.value:
            pass
        else:
            errors.append(BlockError(name, f"Unknown evaluate string: {raw_eval_type}"))
        # Description
        description = block.get("description", "")
        # Get depends on
        depends_on = block.get("depends_on", [])
        if not errors:
            block_obj = cls(
                name,
                rules,
                eval_type=eval_type,
                depends_on=depends_on,
                variables=variables,
                description=description,
            )
        return block_obj, errors

    def to_dict(self) -> t.Dict:
        """Dump block as a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "evaluate": self.eval_type.value,
            "depends_on": self.depends_on,
            "variables": getattr(self, "orig_variables", {}),
            "rules": [rule.to_dict() for rule in self.rules],
        }
