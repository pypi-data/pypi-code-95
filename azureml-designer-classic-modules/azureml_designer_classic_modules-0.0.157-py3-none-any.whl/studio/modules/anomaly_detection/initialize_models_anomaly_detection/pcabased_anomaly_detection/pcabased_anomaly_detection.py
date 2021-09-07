import numpy as np
import pandas as pd
from nimbusml import Pipeline
from nimbusml.decomposition import PcaAnomalyDetector

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import ErrorMapping, InvalidTrainingDatasetError
from azureml.studio.common.parameter_range import (ParameterRangeSettings,
                                                   Sweepable)
from azureml.studio.core.logger import TimeProfile
from azureml.studio.modulehost.attributes import (BooleanParameter,
                                                  IntParameter, ModeParameter,
                                                  ModuleMeta,
                                                  ParameterRangeParameter,
                                                  ReleaseState,
                                                  UntrainedLearnerOutputPort)
from azureml.studio.modulehost.module_reflector import BaseModule, module_entry
from azureml.studio.modules.anomaly_detection.common.base_anomaly_detection import (
    BaseAnomalyDetectionLearner, CreateLearnerMode, RestoreInfo)
from azureml.studio.modules.ml.common.base_learner_setting import \
    BaseLearnerSetting


class PCAAnomalyDetectionModelModuleDefaultParameters:
    MODE = CreateLearnerMode.SingleParameter
    RANK = 2
    RANK_RANGE = "2; 4; 6; 8; 10"
    OVERSAMPLING = 2
    OVERSAMPLING_RANGE = "2; 4; 6; 8; 10"
    CENTER = False
    NormalizeFeatures = True


class PCABasedAnomalyDetectionModule(BaseModule):
    _param_keys = {
        "mode": "Training mode",
        "rank": "Number of components to use in PCA",
        "oversampling": "Oversampling parameter for randomized PCA",
        "center": "Enable input feature mean normalization",
        "rank_range": "Range for number of PCA components",
        "oversampling_range": "Range for the oversampling parameter used in randomized PCA",
    }

    @staticmethod
    @module_entry(ModuleMeta(
        name="PCA-Based Anomaly Detection",
        description="Create a PCA-based anomaly detection model.",
        category="Anomaly Detection",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="C3822FA5-1095-4C72-BD1E-FD43D285153A",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Training mode",
                friendly_name="Training mode",
                description="Specify learner options. Use 'SingleParameter' to manually specify all values. "
                            "Use 'ParameterRange' to sweep over tunable parameters.",
                default_value=CreateLearnerMode.SingleParameter,
            ),
            rank: IntParameter(
                name="Number of components to use in PCA",
                friendly_name="Number of components to use in PCA",
                description="Specify the number of components to use in PCA.",
                default_value=2,
                parent_parameter="Training mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            oversampling: IntParameter(
                name="Oversampling parameter for randomized PCA",
                friendly_name="Oversampling parameter for randomized PCA",
                description="Specify the accuracy parameter for randomized PCA training.",
                default_value=2,
                parent_parameter="Training mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=0,
            ),
            center: BooleanParameter(
                name="Enable input feature mean normalization",
                friendly_name="Enable input feature mean normalization",
                description="Specify if the input data is normalized to have zero mean. ",
                default_value=False,
            ),
            rank_range: ParameterRangeParameter(
                name="Range for number of PCA components",
                friendly_name="Range for number of PCA components",
                description="Specify the range for number of components to use in PCA.",
                default_value="2; 4; 6; 8; 10",
                parent_parameter="Training mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=100,
                is_int=True,
                is_log=False,
                slider_min=1,
                slider_max=100,
            ),
            oversampling_range: ParameterRangeParameter(
                name="Range for the oversampling parameter used in randomized PCA",
                friendly_name="Range for the oversampling parameter used in randomized PCA",
                description="Specify the range for accuracy parameter used in randomized PCA training.",
                default_value="2; 4; 6; 8; 10",
                parent_parameter="Training mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=100,
                is_int=True,
                is_log=False,
                slider_min=1,
                slider_max=100,
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained PCA-based anomaly detection model.",
            ),
    ):
        input_values = locals()
        output_values = PCABasedAnomalyDetectionModule.run_impl(**input_values)
        return output_values

    @classmethod
    def run_impl(
            cls,
            mode: CreateLearnerMode,
            rank: int,
            oversampling: int,
            center: bool,
            rank_range: ParameterRangeSettings = None,
            oversampling_range: ParameterRangeSettings = None,
    ):
        setting = PCAAnomalyDetectionModelSetting()
        if mode == CreateLearnerMode.SingleParameter:
            setting.init_single(
                rank=rank,
                oversampling=oversampling,
                center=center)
        else:
            setting.init_range(
                rank_range=rank_range,
                oversampling_range=oversampling_range,
                center=center
            )
        return PCAAnomalyDetectionModel(setting),


class PCAAnomalyDetectionModelSetting(BaseLearnerSetting):
    def __init__(self):
        super().__init__()
        self.rank = PCAAnomalyDetectionModelModuleDefaultParameters.RANK
        self.oversampling = PCAAnomalyDetectionModelModuleDefaultParameters.OVERSAMPLING
        self.center = PCAAnomalyDetectionModelModuleDefaultParameters.CENTER
        self.normalize_features = PCAAnomalyDetectionModelModuleDefaultParameters.NormalizeFeatures
        self.create_learner_mode = PCAAnomalyDetectionModelModuleDefaultParameters.MODE
        self.parameter_range = {
            'rank': Sweepable.from_prs(
                "rank_range", ParameterRangeSettings.from_literal(
                    PCAAnomalyDetectionModelModuleDefaultParameters.RANK_RANGE)).attribute_value,
            'oversampling': Sweepable.from_prs(
                "oversampling_range", ParameterRangeSettings.from_literal(
                    PCAAnomalyDetectionModelModuleDefaultParameters.OVERSAMPLING_RANGE)).attribute_value
        }

    def init_single(self,
                    rank: int = PCAAnomalyDetectionModelModuleDefaultParameters.RANK,
                    oversampling: int = PCAAnomalyDetectionModelModuleDefaultParameters.OVERSAMPLING,
                    center=PCAAnomalyDetectionModelModuleDefaultParameters.CENTER):
        self.create_learner_mode = CreateLearnerMode.SingleParameter
        self.rank = rank
        self.oversampling = oversampling
        self.center = center

    def init_range(self, rank_range: ParameterRangeSettings = None, oversampling_range: ParameterRangeSettings = None,
                   center=PCAAnomalyDetectionModelModuleDefaultParameters.CENTER):
        self.create_learner_mode = CreateLearnerMode.ParameterRange
        self.add_sweepable(Sweepable.from_prs('rank', rank_range))
        self.add_sweepable(Sweepable.from_prs('oversampling', oversampling_range))


class PCAAnomalyDetectionModel(BaseAnomalyDetectionLearner):
    def __init__(self, setting: PCAAnomalyDetectionModelSetting):
        super().__init__(setting)

    @property
    def parameter_mapping(self):
        return {
            'rank': RestoreInfo(PCABasedAnomalyDetectionModule._args.rank.friendly_name),
            'oversampling': RestoreInfo(PCABasedAnomalyDetectionModule._args.oversampling.friendly_name),
            'center': RestoreInfo(PCABasedAnomalyDetectionModule._args.center.friendly_name)
        }

    def init_model(self):
        self.model = Pipeline([PcaAnomalyDetector(
            rank=self.setting.rank,
            oversampling=self.setting.oversampling,
            center=self.setting.center,
            random_state=42
        )])

    def train(self, data_table: DataTable):
        self._validate_args(data_table)
        super().train(data_table)
        self._verify_trained_model(sample_data=data_table)

    def _verify_trained_model(self, sample_data: DataTable):
        # before making predictions with trained model, nimbusml saves the model to disk and loads it back,
        # if model is invalid, it would raise an runtime error. So we call predict method after training finished to
        # detect invalid model before score module. For details, please refer to this pr:
        # https://github.com/dotnet/machinelearning/pull/5349
        if not self.is_trained:
            return
        sample_x, _ = self.preprocess_training_data(sample_data)
        try:
            self.model.predict(sample_x[:1, :])  # pylint: disable=no-member
        except RuntimeError as e:
            err_message = ErrorMapping.get_exception_message(e)
            if 'One of the identified items was in an invalid format' in err_message:
                ErrorMapping.throw(InvalidTrainingDatasetError(
                    data_name="Dataset",
                    action_name="Training",
                    reason="The learnt eigenvectors contained NaN values",
                    troubleshoot_hint=f'Consider modifying the dataset or lower the '
                    f'"{PCABasedAnomalyDetectionModule._args.rank.friendly_name}" or '
                    f'"{PCABasedAnomalyDetectionModule._args.oversampling.friendly_name}" parameters.'
                ))
            else:
                raise e

    def _predict(self, test_x: pd.DataFrame):
        try:
            with TimeProfile("Predicting probability"):
                # nimbusml.Pipeline test method
                prob = self.model.predict(test_x).values.ravel()  # pylint: disable=no-member
        except Exception as e:
            raise e

        with TimeProfile("calculating argmax(Probability)"):
            # 1 is inlier while 0 outlier as training with only normal data.
            label = np.where(prob >= 0.5, 1, 0)
        return label, prob

    def _validate_args(self, training_data):
        self._record_feature_column_names(training_data)
        ErrorMapping.verify_less_than_or_equal_to(
            value=self.setting.rank,
            b=len(self.init_feature_columns_names),
            arg_name=PCABasedAnomalyDetectionModule._args.rank.friendly_name,
            b_name='the number of feature columns in the dataset')
