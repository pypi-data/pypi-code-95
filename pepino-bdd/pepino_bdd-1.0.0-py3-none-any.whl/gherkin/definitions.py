import inspect
from typing import Callable, Dict, Any, List, Optional, Tuple
import re

from gherkin.parser import Parser

from ..data import DataTable
from .data import GherkinDataTable, GherkinDocString
from .location import GherkinLocation
from ..exceptions import UnknownStepException
from ..definitions import Feature, Scenario, Step, Background, Rule
from ..registry import registry


def scenario_outline_generator(parsed: dict):
    name = parsed["name"]
    tags = parsed["tags"]
    steps = parsed["steps"]
    headers = [
        cell["value"] for cell in parsed["examples"][0]["tableHeader"]["cells"]
    ]
    rows = [
        {headers[idx]: cell["value"] for idx, cell in enumerate(row["cells"])}
        for row in parsed["examples"][0]["tableBody"]
    ]
    for idx, row in enumerate(rows):
        scenario_name = f"{name} #{idx+1}"
        scenario_steps = []
        for step in steps:
            step_text = re.sub(
                "<(.*?)>",
                lambda val: row.get(val.group(1), val.group(0)),
                step["text"],
            )
            scenario_step = step.copy()
            scenario_step["text"] = step_text
            scenario_steps.append(scenario_step)
        scenario_data = {
            "type": "Scenario",
            "location": parsed["location"],
            "tags": tags,
            "name": scenario_name,
            "steps": scenario_steps,
        }
        yield GherkinScenario(scenario_data)


class GherkinStep(Step, GherkinLocation):

    def __init__(self, parsed: dict):
        super(GherkinStep, self).__init__(parsed)
        self._keyword = parsed["keyword"].strip()
        self._text = parsed["text"]
        self.table = None
        self.doc_string = None
        if "dataTable" in parsed:
            self.table = GherkinDataTable(parsed["dataTable"])
        elif "docString" in parsed:
            self.doc_string = GherkinDocString(parsed["docString"])

    @property
    def location(self) -> str:
        return self.position

    @property
    def text(self) -> str:
        return self._text

    @property
    def keyword(self) -> str:
        return self._keyword

    def _match_step(self, pattern: str) -> Tuple[Optional[Callable], Dict]:
        for pat, func in registry.step_dict.items():
            kwargs = {}
            sindex = 0
            pattern_segments = re.split("(<.*?>)", pat)
            for idx, pat_seg in enumerate(pattern_segments):
                if pat_seg:
                    if pat_seg[0] == "<" and pat_seg[-1] == ">":
                        kwarg_name = pat_seg[1:-1]
                        end_index = -1
                        if idx < len(pattern_segments) and pattern_segments[idx + 1]:
                            try:
                                end_index = pattern[sindex:].index(
                                    pattern_segments[idx + 1]
                                )
                            except ValueError:
                                break
                        if end_index > -1:
                            kwargs[kwarg_name] = pattern[sindex: sindex + end_index]
                        else:
                            kwargs[kwarg_name] = pattern[sindex:]
                        sindex += end_index
                    elif pattern[sindex: sindex + len(pat_seg)] == pat_seg:
                        sindex += len(pat_seg)
                    else:
                        break
            else:
                return func, kwargs
        return None, {}

    @property
    def function(self) -> Callable:
        if not hasattr(self, "_func"):
            self._func, self._kwargs = self._match_step(self.text)
        if not self._func:
            raise UnknownStepException(self)
        return self._func

    @property
    def args(self) -> Tuple:
        return ()

    @property
    def kwargs(self) -> dict:
        sig = inspect.signature(self.function)
        kwargs: Dict[str, Any] = self._kwargs
        arg_start = 1 if inspect.ismethod(self.function) else 0
        for idx, p in enumerate(sig.parameters.items()):
            if idx >= arg_start:
                p_name, p_value = p
                if p_value.annotation and p_name in kwargs:
                    kwargs[p_name] = registry.get_type_func(p_value.annotation)(
                        kwargs[p_name]
                    )
                elif (
                    p_value.annotation
                    and p_value.annotation == DataTable
                    and self.table
                ):
                    kwargs[p_name] = self.table
                elif (
                    p_value.annotation and p_value.annotation == str and self.doc_string
                ):
                    kwargs[p_name] = self.doc_string.content
        return kwargs


class GherkinBackground(Background, GherkinLocation):

    def __init__(self, parsed):
        super().__init__(parsed)
        self._name = parsed["name"]
        self._steps = []
        for step in parsed["steps"]:
            self._steps.append(GherkinStep(step))

    @property
    def name(self) -> str:
        return self._name

    @property
    def steps(self):
        return self._steps


class GherkinScenario(Scenario, GherkinLocation):

    def __init__(self, parsed):
        super().__init__(parsed)
        self._name = parsed["name"]
        self._tags = parsed["tags"]
        self._steps = []
        for step in parsed["steps"]:
            self._steps.append(GherkinStep(step))

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def name(self) -> str:
        return self._name

    @property
    def steps(self) -> List[Step]:
        return self._steps


class GherkinRule(Rule, GherkinLocation):

    def __init__(self, parsed):
        super().__init__(parsed)
        self._name = parsed["name"]
        self._tags = parsed["tags"]
        self._description = parsed.get('description', '')
        self._scenarios = []
        for child_dict in parsed["children"]:
            child_type = list(child_dict)[0]
            child = child_dict[child_type]
            if child_type == "scenario" and child["keyword"] == "Scenario":
                self._scenarios.append(GherkinScenario(child))
            elif child_type == "scenario" and child["keyword"] == "Scenario Outline":
                self._scenarios.extend(list(scenario_outline_generator(child)))

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def scenarios(self) -> List[Scenario]:
        return self._scenarios


class GherkinFeature(Feature, GherkinLocation):

    def __init__(self, parsed):
        super().__init__(parsed)
        self._name = parsed["name"]
        self._tags = [tag['name'][1:] for tag in parsed["tags"]]
        self._description = parsed.get("description", "")
        self._background = None
        self._scenarios = []
        self._rules = []
        for child_dict in parsed["children"]:
            child_type = list(child_dict)[0]
            child = child_dict[child_type]
            if child_type == "background":
                self._background = GherkinBackground(child)
            elif child_type == "scenario" and child["keyword"] == "Scenario":
                self._scenarios.append(GherkinScenario(child))
            elif child_type == "scenario" and child["keyword"] == "Scenario Outline":
                self._scenarios.extend(list(scenario_outline_generator(child)))
            elif child_type == "rule":
                self._rules.append(GherkinRule(child))
            else:
                raise Exception(f'Unkown child type: {child_type}')

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def background(self) -> Optional[Background]:
        return self._background

    @property
    def scenarios(self) -> List[Scenario]:
        return self._scenarios

    @property
    def rules(self) -> List[Rule]:
        return self._rules

    @classmethod
    def from_string(cls, feature_string):
        gherkin_parser = Parser()
        return GherkinFeature(gherkin_parser.parse(feature_string)["feature"])
