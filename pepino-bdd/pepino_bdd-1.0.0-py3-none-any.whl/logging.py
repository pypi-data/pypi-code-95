import logging
import traceback
from termcolor import colored

from .registry import CucumberRegistry
from .enums import Hook, Result
from . import definitions
from .results import StepResult

Logger = logging.getLogger(__name__)


class LoggingHook(object):

    def log_pre_feature(self, feature: definitions.Feature):
        description = "\n".join(
            [f"\t{line.strip()}" for line in feature.description.split("\n")]
        )
        print(f"\n{colored('Feature:', attrs=['bold'])} {feature.name}\n{description}")  # noqa

    def log_pre_scenario(self, scenario: definitions.Scenario):
        print(f"\n\n\t{colored('Scenario:', attrs=['bold'])} {scenario.name}")  # noqa

    def log_pre_background(self, background: definitions.Background):
        print(f"\n\n\t{colored('Background:', attrs=['bold'])} {background.name}")  # noqa

    def log_pre_step(self, step: definitions.Step):
        print(f"\t\t{step.text}", end="\r")  # noqa

    def log_post_step(self, result: StepResult):
        time = colored(f"({result.duration.total_seconds():.2f}s)", attrs=["bold"])  # type: ignore
        colour = "green" if result.result == Result.PASSED else "red"
        print(f"\t\t{colored(result.step.text, colour)} {time}", end="\n")  # noqa
        if result.result == Result.FAILED and result.exc_info is not None:
            print(f"\n\t\t{colored(str(result.exc_info[1]), 'red', attrs=['bold'])}")  # noqa
            tb = traceback.format_exception(*result.exc_info)  # type: ignore
            for line in tb:
                parts = line[:-1].split("\n")
                exc_line = colored(parts[0], attrs=["bold"])
                print(f"\t\t{exc_line}")  # noqa
                if len(parts) > 1:
                    for part in parts[1:]:
                        print(f"\t\t\t{part}")  # noqa

    def initialise(self, registry: CucumberRegistry):
        registry.add_hook(Hook.pre_feature, self.log_pre_feature)
        registry.add_hook(Hook.pre_background, self.log_pre_background)
        registry.add_hook(Hook.pre_scenario, self.log_pre_scenario)
        registry.add_hook(Hook.pre_step, self.log_pre_step)
        registry.add_hook(Hook.post_step, self.log_post_step)
