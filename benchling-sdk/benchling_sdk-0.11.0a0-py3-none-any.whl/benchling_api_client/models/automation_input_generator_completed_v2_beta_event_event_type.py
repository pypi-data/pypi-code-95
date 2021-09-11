from enum import Enum


class AutomationInputGeneratorCompletedV2BetaEventEventType(str, Enum):
    V2_BETAAUTOMATIONINPUTGENERATORCOMPLETED = "v2-beta.automationInputGenerator.completed"

    def __str__(self) -> str:
        return str(self.value)
