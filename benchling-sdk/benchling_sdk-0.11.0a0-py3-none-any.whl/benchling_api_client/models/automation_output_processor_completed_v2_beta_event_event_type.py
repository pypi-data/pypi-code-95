from enum import Enum


class AutomationOutputProcessorCompletedV2BetaEventEventType(str, Enum):
    V2_BETAAUTOMATIONOUTPUTPROCESSORCOMPLETED = "v2-beta.automationOutputProcessor.completed"

    def __str__(self) -> str:
        return str(self.value)
