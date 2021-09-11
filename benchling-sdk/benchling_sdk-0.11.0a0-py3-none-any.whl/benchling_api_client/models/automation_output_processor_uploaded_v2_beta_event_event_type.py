from enum import Enum


class AutomationOutputProcessorUploadedV2BetaEventEventType(str, Enum):
    V2_BETAAUTOMATIONOUTPUTPROCESSORUPLOADED = "v2-beta.automationOutputProcessor.uploaded"

    def __str__(self) -> str:
        return str(self.value)
