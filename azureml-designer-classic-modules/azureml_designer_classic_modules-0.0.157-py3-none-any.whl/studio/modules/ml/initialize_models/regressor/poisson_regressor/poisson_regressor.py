import pandas as pd
from nimbusml.linear_model import PoissonRegressionRegressor
from azureml.studio.common.datatable.constants import ColumnTypeName
from azureml.studio.common.error import ErrorMapping, InvalidTrainingDatasetError
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.core.logger import TimeProfile, module_logger
from azureml.studio.modulehost.attributes import ModeParameter, FloatParameter, IntParameter, BooleanParameter, \
    ParameterRangeParameter, UntrainedLearnerOutputPort, ModuleMeta
from azureml.studio.internal.attributes.release_state import ReleaseState
from azureml.studio.modulehost.constants import FLOAT_MIN_POSITIVE, FLOAT_MAX
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import TaskType, CreateLearnerMode, RestoreInfo
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting
from azureml.studio.modules.ml.common.supervised_learners import RegressionLearner


class DefaultParameters:
    Mode = CreateLearnerMode.SingleParameter
    OptimizationTolerance = 1e-07
    L1Weight = 1.0
    L2Weight = 1.0
    MemorySize = 20
    PsOptimizationTolerance = "0.00001; 0.00000001"
    PsL1Weight = "0.0; 0.01; 0.1; 1.0"
    PsL2Weight = "0.01; 0.1; 1.0"
    PsMemorySize = "5; 20; 50"
    RandomNumberSeed = None
    AllowUnknownLevels = True


class PoissonRegressionModule(BaseModule):
    @staticmethod
    @module_entry(
        ModuleMeta(
            name="Poisson Regression",
            description="Creates a regression model that assumes data has a Poisson distribution",
            category="Machine Learning Algorithms/Regression",
            version="2.0",
            owner="Microsoft Corporation",
            family_id="80E21B9D-3827-40D8-B733-B53148BECBC2",
            release_state=ReleaseState.Release,
            is_deterministic=True,
        )
    )
    def run(
            mode: ModeParameter(
                CreateLearnerMode,
                name="Create trainer mode",
                friendly_name="Create trainer mode",
                description="Create advanced learner options",
                default_value=DefaultParameters.Mode,
            ),
            optimization_tolerance: FloatParameter(
                name="Tolerance parameter for optimization convergence "
                     "the lower the value the slower and more accurate the fitting",
                friendly_name="Optimization tolerance",
                description="Specify a tolerance value for optimization convergence. "
                            "The lower the value, the slower and more accurate the fitting.",
                default_value=DefaultParameters.OptimizationTolerance,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=FLOAT_MIN_POSITIVE,
            ),
            l1_weight: FloatParameter(
                name="L1 regularization weight",
                friendly_name="L1 regularization weight",
                description="Specify the L1 regularization weight. "
                            "Use a non-zero value to avoid overfitting the model.",
                default_value=DefaultParameters.L1Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=0,
            ),
            l2_weight: FloatParameter(
                name="L2 regularization weight",
                friendly_name="L2 regularization weight",
                description="Specify the L2 regularization weight. "
                            "Use a non-zero value to avoid overfitting the model.",
                default_value=DefaultParameters.L2Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=0,
            ),
            memory_size: IntParameter(
                name="Memory size for L-BFGS the lower the value the faster and less accurate the training",
                friendly_name="Memory size for L-BFGS",
                description="Indicate how much memory (in MB) to use for the L-BFGS optimizer. "
                            "With less memory, training is faster but less accurate the training.",
                default_value=DefaultParameters.MemorySize,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.SingleParameter,),
                min_value=1,
            ),
            ps_optimization_tolerance: ParameterRangeParameter(
                name="Range for optimization tolerance",
                friendly_name="Optimization tolerance",
                description="Specify a range for the tolerance value for the L-BFGS optimizer",
                default_value=DefaultParameters.PsOptimizationTolerance,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=FLOAT_MIN_POSITIVE,
                max_limit=FLOAT_MAX,
                is_int=False,
                is_log=True,
                slider_min=1E-07,
                slider_max=0.001,
            ),
            ps_l1_weight: ParameterRangeParameter(
                name="Range for L1 regularization weight",
                friendly_name="L1 regularization weight",
                description="Specify the range for the L1 regularization weight. "
                            "Use a non-zero value to avoid overfitting.",
                default_value=DefaultParameters.PsL1Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=0,
                max_limit=FLOAT_MAX,
                is_int=False,
                is_log=True,
                slider_min=0.0001,
                slider_max=1,
            ),
            ps_l2_weight: ParameterRangeParameter(
                name="Range for L2 regularization weight",
                friendly_name="L2 regularization weight",
                description="Specify the range for the L2 regularization weight. "
                            "Use a non-zero value to avoid overfitting.",
                default_value=DefaultParameters.PsL2Weight,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=0,
                max_limit=FLOAT_MAX,
                is_int=False,
                is_log=True,
                slider_min=0.0001,
                slider_max=1,
            ),
            ps_memory_size: ParameterRangeParameter(
                name="Range for memory size for L-BFGS the lower the value the faster and less accurate the training",
                friendly_name="Memory size for L-BFGS",
                description="Specify the range for the amount of memory (in MB) to use for the L-BFGS optimizer. "
                            "The lower the value, the faster and less accurate the training.",
                default_value=DefaultParameters.PsMemorySize,
                parent_parameter="Create trainer mode",
                parent_parameter_val=(CreateLearnerMode.ParameterRange,),
                min_limit=1,
                max_limit=2147483647,
                is_int=True,
                is_log=False,
                slider_min=1,
                slider_max=100,
            ),
            random_number_seed: IntParameter(
                name="Random number seed",
                friendly_name="Random number seed",
                is_optional=True,
                description="Type a value to seed the random number generator used by the model. "
                            "Leave blank for default.",
                release_state=ReleaseState.Alpha,
            ),
            allow_unknown_levels: BooleanParameter(
                name="Allow unknown levels in categorical features",
                friendly_name="Allow unknown categorical levels",
                description="Indicate whether an additional level should be created for each categorical column. "
                            "Any levels in the test dataset not available in the training dataset "
                            "are mapped to this additional level.",
                default_value=DefaultParameters.AllowUnknownLevels,
                release_state=ReleaseState.Alpha,
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="An untrained Poisson regression model",
            ),
    ):
        setting = PoissonRegressorSetting.init(**locals())
        return tuple([PoissonRegressor(setting)])


class PoissonRegressorSetting(BaseLearnerSetting):
    def __init__(self, mode: DefaultParameters.Mode,
                 optimization_tolerance: float = DefaultParameters.OptimizationTolerance,
                 l1_weight: float = DefaultParameters.L1Weight,
                 l2_weight: float = DefaultParameters.L2Weight,
                 memory_size: int = DefaultParameters.MemorySize,
                 ps_optimization_tolerance=ParameterRangeSettings.from_literal(
                     DefaultParameters.PsOptimizationTolerance),
                 ps_l1_weight=ParameterRangeSettings.from_literal(DefaultParameters.PsL1Weight),
                 ps_l2_weight=ParameterRangeSettings.from_literal(DefaultParameters.PsL2Weight),
                 ps_memory_size=ParameterRangeSettings.from_literal(DefaultParameters.PsMemorySize),
                 ):
        """Initialize a poisson regression model

        :param optimization_tolerance: float, tolerance value for the L-BFGS optimizer
        :param l1_weight: float, l1 regularization weight.
        :param l2_weight: float, l2 regularization weight.
        :param memory_size: int, memory size for L-BFGS
        :param ps_optimization_tolerance: ParameterRange, range of the tolerance value for the L-BFGS optimizer
        :param ps_l1_weight: ParameterRange, range of the l1 regularization weight.
        :param ps_l2_weight: ParameterRange, range of the l2 regularization weight.
        :param ps_memory_size: ParameterRange, range of the memory size for L-BFGS
        """
        super().__init__()
        name_mapping = {
            'optimization_tolerance': ps_optimization_tolerance,
            'l1_regularization': ps_l1_weight,
            'l2_regularization': ps_l2_weight,
            'history_size': ps_memory_size,
        }
        self.create_learner_mode = mode
        self.optimization_tolerance = optimization_tolerance
        self.l1_weight = l1_weight
        self.l2_weight = l2_weight
        self.memory_size = memory_size
        self.parameter_range = {
            name: self.get_sweepable(name, literal_value) for name, literal_value in name_mapping.items()}

    @staticmethod
    def init(mode, optimization_tolerance, l1_weight, l2_weight, memory_size, ps_optimization_tolerance, ps_l1_weight,
             ps_l2_weight, ps_memory_size, random_number_seed, allow_unknown_levels
             ):
        if mode == CreateLearnerMode.SingleParameter:
            setting = PoissonRegressorSetting.init_single(
                optimization_tolerance=optimization_tolerance,
                l1_weight=l1_weight,
                l2_weight=l2_weight,
                memory_size=memory_size)
        else:
            setting = PoissonRegressorSetting.init_range(
                ps_optimization_tolerance=ps_optimization_tolerance,
                ps_l1_weight=ps_l1_weight,
                ps_l2_weight=ps_l2_weight,
                ps_memory_size=ps_memory_size)
        return setting

    @staticmethod
    def init_single(
            optimization_tolerance: float = DefaultParameters.OptimizationTolerance,
            l1_weight: float = DefaultParameters.L1Weight,
            l2_weight: float = DefaultParameters.L2Weight,
            memory_size: int = DefaultParameters.MemorySize,
    ):
        setting = PoissonRegressorSetting(mode=CreateLearnerMode.SingleParameter, **locals())
        return setting

    @staticmethod
    def init_range(
            ps_optimization_tolerance: ParameterRangeSettings = None,
            ps_l1_weight: ParameterRangeSettings = None,
            ps_l2_weight: ParameterRangeSettings = None,
            ps_memory_size: ParameterRangeSettings = None,
    ):
        setting = PoissonRegressorSetting(mode=CreateLearnerMode.ParameterRange, **locals())
        return setting


class PoissonRegressor(RegressionLearner):
    def __init__(self, setting: PoissonRegressorSetting):
        super().__init__(setting=setting, task_type=TaskType.Regression)

    @property
    def parameter_mapping(self):
        return {
            'optimization_tolerance': RestoreInfo(PoissonRegressionModule._args.optimization_tolerance.friendly_name),
            'l1_regularization': RestoreInfo(PoissonRegressionModule._args.l1_weight.friendly_name),
            'l2_regularization': RestoreInfo(PoissonRegressionModule._args.l2_weight.friendly_name),
            'history_size': RestoreInfo(PoissonRegressionModule._args.memory_size.friendly_name)
        }

    def init_model(self):
        self.model = PoissonRegressionRegressor(
            l1_regularization=self.setting.l1_weight,
            l2_regularization=self.setting.l2_weight,
            optimization_tolerance=self.setting.optimization_tolerance,
            history_size=self.setting.memory_size)

    def _train(self, train_x, train_y):
        # train model
        with TimeProfile("Training Model"):
            train_y = train_y.values if isinstance(train_y, pd.Series) else train_y
            self.model.fit(train_x, train_y)
        self._is_trained = True

    def _predict(self, test_x: pd.DataFrame):
        try:
            with TimeProfile("Predicting regression value"):
                # nimbusml.Pipeline test method
                return self.model.predict(test_x).values.ravel(), None
        except Exception as e:
            raise e

    def check_label_column(self, data_table):
        super().check_label_column(data_table)
        label_column_type = data_table.get_column_type(self.label_column_name)
        # Fix bug 886816: ensure label column type to be numeric before negative value validation
        if label_column_type == ColumnTypeName.NUMERIC:
            label_series = data_table.get_column(self.label_column_name).dropna()
            # Counts cannot be negative. The method will throw exception outright if with negative labels.
            for value in label_series:
                if value < 0:
                    module_logger.info(f"Poisson regressor is trained with a negative expected value: {value}")
                    ErrorMapping.throw(InvalidTrainingDatasetError(
                        data_name='Dataset' if data_table.name is None else data_table.name,
                        learner_type="Poisson Regression",
                        reason=f'Poisson regressor cannot be trained on negative expected values, '
                        f'but label {value} encountered'))
