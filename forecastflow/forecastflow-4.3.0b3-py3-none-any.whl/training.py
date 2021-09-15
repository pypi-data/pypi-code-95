import logging
from typing import List, Optional

from .enums import ClassificationMetrics, RegressionMetrics

from abc import abstractmethod, ABCMeta

logger = logging.getLogger(__name__)


class TrainingSettings(metaclass=ABCMeta):
    """
    Base class for TrainingSettings
    """

    def __init__(
        self,
        target: str,
        primary_id: str,
        secondary_ids: Optional[List[str]] = None,
        feature_excludes: Optional[List[str]] = None,
        random_state: Optional[int] = None,
    ):
        self.target = target
        self.primary_id = primary_id
        self.secondary_ids = secondary_ids
        self.feature_excludes = feature_excludes
        self.random_state = random_state

    @abstractmethod
    def to_dict(self):
        data = {
            'target': self.target,
            'primaryID': self.primary_id,
        }
        if self.secondary_ids is not None:
            data['secondaryIDs'] = self.secondary_ids
        if self.feature_excludes is not None:
            data['featureExcludes'] = self.feature_excludes
        if self.random_state is not None:
            data['randomState'] = self.random_state
        return data


class ClassifierTrainingSettings(TrainingSettings):
    """
    Classifier training settings

    Args:
        target:
            Name of the column which should be predicted
        metric:
            forecastflow.enums.ClassificationMetrics object
        primary_id:
            Name of the primary ID column
        secondary_ids:
            Names list of the secondary ID columns
        feature_excludes:
            Names list of excluded columns
        random_state:
            Seed to the random generator
    """

    def __init__(
        self,
        target: str,
        metric: ClassificationMetrics,
        primary_id: str,
        secondary_ids: Optional[List[str]] = None,
        feature_excludes: List[str] = None,
        random_state: Optional[int] = None,
    ):
        if not isinstance(metric, ClassificationMetrics):
            raise TypeError
        super().__init__(
            target=target,
            primary_id=primary_id,
            secondary_ids=secondary_ids,
            feature_excludes=feature_excludes,
            random_state=random_state,
        )
        self.metric = metric

    def to_dict(self):
        data = super().to_dict()
        data['modelType'] = 'Classification'
        data['metric'] = self.metric.value
        return data


class RegressorTrainingSettings(TrainingSettings):
    """
    Regressor training settings

    Args:
        target:
            Name of the column which should be predicted
        metric:
            forecastflow.enums.RegressionMetrics object
        primary_id:
            Name of the primary ID column
        secondary_ids:
            Names list of the secondary ID columns
        feature_excludes:
            Names list of excluded columns
        random_state:
            Seed to the random generator
    """

    def __init__(
        self,
        target: str,
        metric: ClassificationMetrics,
        primary_id: str,
        secondary_ids: Optional[List[str]] = None,
        feature_excludes: List[str] = None,
        random_state: Optional[int] = None,
    ):
        if not isinstance(metric, RegressionMetrics):
            raise TypeError
        super().__init__(
            target=target,
            primary_id=primary_id,
            secondary_ids=secondary_ids,
            feature_excludes=feature_excludes,
            random_state=random_state,
        )
        self.metric = metric

    def to_dict(self):
        data = super().to_dict()
        data['modelType'] = 'Regression'
        data['metric'] = self.metric.value
        return data


__all__ = [
    'TrainingSettings',
    'ClassifierTrainingSettings',
    'RegressorTrainingSettings',
]
