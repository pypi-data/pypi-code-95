# Copyright 2021 Hylke C. Donker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
from datetime import time
from typing import Callable, Dict, List, Optional, Tuple, Union

from lifelines import KaplanMeierFitter
from lifelines.utils import concordance_index

import numpy as np
from numpy import (
    all,
    any,
    append,
    array,
    bool_,
    column_stack,
    ascontiguousarray,
    copy,
    exp,
    float64,
    full_like,
    inf,
    isnan,
    log,
    logaddexp,
    nanmean,
    ones,
    ones_like,
    pi,
    random,
    sqrt,
    sum,
    take,
    unique,
    where,
    zeros,
    zeros_like,
)
import pandas as pd
from scipy.integrate import nquad
from scipy.special import expit as sigmoid
from scipy.optimize import fsolve
from sklearn.metrics import mean_squared_error
from sklearn.utils.validation import check_is_fitted

from harmoniums.const import Matrix, MatrixPair, MatrixTriplet, ObservationMatrix
from harmoniums.const import ObservationTriplet as Observation
from harmoniums.distributions import (
    fit_truncated_gamma_parameters,
    log_normalisation_gamma_distribution,
    normalisation_gamma_interval_distribution,
    normalisation_gamma_distribution,
)

from harmoniums.functional_math import (
    _lambda_partition_function_i,
    _partition_function_i,
)
from harmoniums import BaseHarmonium
from harmoniums.samplers import (
    sample_interval_truncated_gamma_distribution,
    sample_right_truncated_gamma_distribution,
)
from harmoniums.utils import (
    brier_loss,
    check_arrays,
    generate_binary_permutations,
    get_columns,
    hash_array,
    reset_random_state,
)


class SurvivalHarmonium(BaseHarmonium):
    """
    Harmonium that jointly models categorical (A), survival (B), and numerical (C) data.
    """

    parameters = (
        # Parameters categorical data.
        "W_A",
        "a_A",
        # Parameteres time-to-event data.
        "W_B",
        "V",
        "a_B",
        "c",
        # Parameters numerical data.
        "W_C",
        "a_C",
        "sigma",
        # Latent bias.
        "b",
    )
    # By default, don't apply weight decay to bias and standard deviation
    # parameters (see Hinton RBM tutorial).
    no_penalty = ("a_A", "a_B", "a_C", "b", "c", "sigma")

    def __init__(
        self,
        # Number of (binary valued) latent states.
        n_hidden_units: int = 1,
        # What initial values to use for the Gibbs chain of the missing values.
        fill_nan_method: Callable = nanmean,
        # The risk is defined as the survival distribution evaluated at a
        # particular time point. This argument control the time point by
        # (i) setting a value for each survival variable, or
        # (ii) using the median value using Kaplan-Meier, or
        # (iii) another function that is evaluated over the training set.
        risk_score_time_point: Union[Callable, float, str] = "median",
        # Columns of the time-to-event variables.
        survival_columns=[],
        # Event indicator columns of the respective survival variables.
        event_columns=[],
        # Columns of the time-independent numeric variables.
        numeric_columns=[],
        # Columns of the categorical (i.c., binary) variables.
        categorical_columns=[],
        # Scale of weights is ~ 1e-2, the learning rate is a factor 1e-3 smaller than
        # that [1].
        learning_rate: Union[float, Tuple[float, ...], list, dict] = 1e-3,
        # Time range to model. Can be a list for each event variable seperately,
        # a float to fit the horizon as max(t)*`time_horizon`, or `None` to
        # indicate that no scaling is necessary.
        time_horizon: Optional[Union[list, float]] = 2.0,
        random_state: int = 1234,
        # Number of contrastive divergence steps.
        CD_steps: int = 1,
        # Use this much from the previous update.
        momentum_fraction: float = 0.0,
        weight_decay: float = 0.0,
        mini_batch_size: int = 50,
        n_epochs: int = 10,
        log_every_n_iterations: Optional[int] = 25,
        maximum_iteration: int = -1,
        tolerance: float = 1.0e-12,
        persistent: bool = False,
        verbose: bool = False,
        # Metrics to calculate during training.
        metrics: Tuple[str, ...] = tuple(),
        # Validation data for which to calculate the metrics.
        X_validation: Optional[Matrix] = None,
        # Initialise parameters by calling `fit`, but don't run constrative divergence.
        dry_run: bool = False,
        guess_weights: Union[bool, str] = False,
        # Helper parameters so that some internal functions can be used without
        # fitting the data.
        n_categorical_units: int = 0,
        n_event_units: int = 0,
        n_numeric_units: int = 0,
    ):
        self.n_hidden_units = n_hidden_units
        self.n_categorical_units = n_categorical_units
        self.n_event_units = n_event_units
        self.n_numeric_units = n_numeric_units
        self.fill_nan_method = fill_nan_method
        self.CD_steps = CD_steps
        self.mini_batch_size = mini_batch_size
        self.n_epochs = n_epochs
        self.maximum_iteration = maximum_iteration
        self.tolerance = tolerance
        self.verbose = verbose
        self.log_every_n_iterations = log_every_n_iterations
        self.persistent = persistent
        self.dry_run = dry_run
        self.momentum_fraction = momentum_fraction
        self.weight_decay = weight_decay
        self.X_validation = X_validation
        self.guess_weights = guess_weights
        self.metrics = metrics
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.time_horizon = time_horizon
        self.categorical_columns = categorical_columns
        self.survival_columns = survival_columns
        self.numeric_columns = numeric_columns
        self.event_columns = event_columns
        self.risk_score_time_point = risk_score_time_point

    def _more_tags(self) -> dict:
        """
        Tags for scikit-learn estimator.
        """
        return {
            # For `check_estimator`, when a single matrix is passed to fit.
            "requires_positive_X": True,
            # Act as if event indicators are binary labels.
            "binary_only": True,
        }

    def _normalise(self, X: Matrix, copy: bool = True) -> Matrix:
        """
        Normalise the time-to-event variables using the time horizon.
        """
        if copy:
            X = X.copy()

        XI_B = get_columns(X, self.survival_columns)
        # Normalise to [0, 1] range.
        time_horizon = getattr(self, "time_horizon_", 1.0)

        if any(XI_B / time_horizon > 1.0):
            raise ValueError("Time-to-event variables extend beyond the time horizon!")

        X = self._set_columns(X, XI_B / time_horizon, self.survival_columns)

        return X

    def _unpack(
        self, X: Optional[Matrix], normalise=True, verify=True
    ) -> Tuple[MatrixTriplet, Matrix]:
        """
        Unpack matrix as observation pair o=(xi, event).
        """
        if normalise and self.n_event_units > 0:
            X = self._normalise(X)

        X_A = get_columns(X, self.categorical_columns)
        X_B = get_columns(X, self.survival_columns)
        X_C = get_columns(X, self.numeric_columns)

        # Reshape empty arrays to size m x 0.
        m = self.get_number_of_rows((X_A, X_B, X_C))
        XI = (X_A.reshape(m, -1), X_B.reshape(m, -1), X_C.reshape(m, -1))

        event = get_columns(X, self.event_columns, dtype=bool_)

        # Check that the data admits to the bounds.
        if normalise and verify and self.n_event_units > 0:
            if event.size == 0:
                event = ones_like(X_B, order="C", dtype=bool_)
            # Time-to-event variables must be strictly > 0 when observed,
            # or >= 0 when censored.
            assert all((X_B > 0) | ((X_B >= 0) & ~event))
            assert all(X_B <= 1)

        return XI, event

    def _compress(self, xi: MatrixTriplet, event: Matrix, renormalise=True) -> Matrix:
        """
        Inverse operation of `_unpack`.
        """
        m = self.get_number_of_rows(xi)
        n = self.n_categorical_units + self.n_numeric_units + 2 * self.n_event_units

        if (
            (self.categorical_columns and isinstance(self.categorical_columns[0], str))
            or (self.survival_columns and isinstance(self.survival_columns[0], str))
            or (self.numeric_columns and isinstance(self.numeric_columns[0], str))
        ):
            X = pd.DataFrame()
        else:
            X = zeros(shape=[m, n])

        X = self._set_columns(X, xi[0], self.categorical_columns)
        if renormalise and self.survival_columns:
            time_horizon = getattr(self, "time_horizon_", 1.0)
            X = self._set_columns(X, xi[1] * time_horizon, self.survival_columns)
        else:
            X = self._set_columns(X, xi[1], self.survival_columns)
        X = self._set_columns(X, event, self.event_columns)
        X = self._set_columns(X, xi[2], self.numeric_columns)

        return X

    def initialise_parameters(self, X: Optional[Matrix] = None):
        """
        Initialise training parameteres, possibly using training data `X`.

        This method should set `is_parameters_initialised_` to True.
        """

        # These array settings are required for low level Numba math (see
        # functional_math.py).
        numpy_args = {
            "dtype": float64,
            # Contiguous memory layout.
            "order": "C",
        }

        # 1) Initialise categorical parameters (group A).
        # Weight initialisations of `W` according to Hinton.
        self.W_A = random.normal(
            0.0, 0.01, size=(self.n_categorical_units, self.n_hidden_units)
        )
        self.a_A = zeros(shape=(self.n_categorical_units, 1), **numpy_args)
        if X is not None and self.n_categorical_units > 0:
            (
                XI_A,
                _,
                _,
            ), _ = self._unpack(X, normalise=True)
            # Initialise the bias using probabilities.
            p = nanmean(XI_A, axis=0, keepdims=True).T
            # Set visible units according to ln[p/(1-p)], see Ref. [1].
            self.a_A = log(p / (1 - p), out=zeros_like(p), where=(p != 0) & (p != 1))

        # 2) Initialise time-to-event parameters (group B).
        # Glorot-Bengio weight initialisations.
        scale_GB = sqrt(6 / (self.n_hidden_units + self.n_event_units))
        self.W_B = random.uniform(
            -scale_GB, scale_GB, size=(self.n_event_units, self.n_hidden_units)
        )
        # Multiply GB scale by 2 to account for asymmetry.
        self.V = random.uniform(
            0, 2 * scale_GB, size=(self.n_event_units, self.n_hidden_units)
        )
        self.c = random.uniform(0, 2 * scale_GB, size=(self.n_event_units, 1))

        self.a_B = zeros((self.n_event_units, 1), **numpy_args)
        # Multiply GB scale by 2 to account for asymmetry.
        if X is not None and self.n_event_units > 0:
            (
                _,
                XI_B,
                _,
            ), _ = self._unpack(X, normalise=True)
            # Expect bias when half the latent states turn on.
            Vh_exp = sum(self.V, axis=1, keepdims=True) / 2

            # Use statistics from the gamma distribution defined on [0, infty].
            if self.guess_weights == "asymptotic" or self.guess_weights is True:
                mu = XI_B.mean(axis=0, keepdims=True).T
                sigma = XI_B.std(axis=0, keepdims=True).T
                # <x> = alpha/beta.
                # <x^2> - <x>^2 = alpha/beta^2.
                beta = mu / sigma ** 2
                alpha = mu ** 2 / sigma ** 2
                # Set visible biases.
                self.c = np.where(alpha != 0.0, alpha, self.c) - Vh_exp
                self.a_B = beta
            elif self.guess_weights == "truncated_gamma":
                try:
                    alpha, beta = fit_truncated_gamma_parameters(XI_B)
                except NotImplementedError:
                    print("Warning: Unable to find good initialisation parameters.")
                else:
                    self.a_B = beta.reshape(-1, 1)
                    self.c = (
                        np.where(alpha != 0.0, alpha, self.c.flatten()).reshape(-1, 1)
                        - Vh_exp
                    )

        # 3) Initialise parameters of numerical features (group C).
        self.W_C = random.uniform(
            -scale_GB,
            scale_GB,
            size=(self.n_numeric_units, self.n_hidden_units),
        )
        self.sigma = ones(shape=(self.n_numeric_units, 1), **numpy_args)
        # TODO [#40]: Use more clever initialisation for bias.
        self.a_C = zeros((self.n_numeric_units, 1), **numpy_args)

        # 4) Initialise bias.
        self.b = zeros((self.n_hidden_units, 1), **numpy_args)

        self.is_parameters_initialised_ = True

    def initialise_nan_substitutions(self, X: Matrix):
        """
        Calculate NaN value substitutions for the Gibbs chain starting point.
        """
        if isinstance(X, pd.DataFrame):
            # Workaround for NumPy bug
            # https://github.com/numpy/numpy/issues/10393. Instead of doing:
            # self.fill_nan_ = X.apply(self.fill_nan_method, ..)
            #
            self.fill_nan_ = pd.DataFrame(
                {
                    c: self.fill_nan_method(X[c], axis=0, keepdims=True)
                    for c in X.columns
                }
            )
        else:
            self.fill_nan_ = self.fill_nan_method(X, axis=0, keepdims=True)
        if any(np.nan == self.fill_nan_):
            raise ValueError("Probably incorrect `fill_nan_method` method.")

    def phi(self, X: MatrixTriplet) -> Matrix:
        """
        Latent state bias, large positive (negative) `phi` (de)activates the state.

        Args:
            X: Tuple of states (with shape Matrix[m x n_v(i)]) corresponding to
                categorical, event, and numeric variables, respectively.
        Returns:
            Matrix[m x n_h]: Bias of the hidden units.
        """
        X_A, X_B, X_C = X
        # return _phi(
        #     X_A, X_B, X_C, self.W_A, self.W_B, self.W_C, self.V, self.sigma, self.b,
        # )
        # Binary model: sum_i x_i W_ij
        phi_A = X_A @ self.W_A

        # Gamma model: sum_i x_i W_ij - log[x_i] |V_ij|
        # Take log safely, by replacing 0 values with large instead of `inf`
        # number.
        phi_B = X_B @ self.W_B - log(
            X_B, where=X_B > 0, out=-32 * ones_like(X_B)
        ) @ abs(self.V)

        # Gauss model: sum_i x_i W_ij/sigma_i
        phi_C = X_C / self.sigma.T @ self.W_C

        # And the overall bias.
        return self.b.T + phi_A + phi_B + phi_C

    def alpha_beta(self, H: Matrix) -> MatrixPair:
        """
        Calculate shape (alpha) and rate (beta) parameters of the Gamma distribution.

        alpha(i) - 1 = sum_j|V(i,j)|h_j + |c_i| ln[x_i],
        beta(i) = sum_j W(i,j)h_j + a_i.
        """
        # Calculate alpha and beta from activations.
        ALPHA = H @ abs(self.V.T) + abs(self.c.T) + 1
        BETA = H @ self.W_B.T + self.a_B.T
        return (ALPHA, BETA)

    def z(self, H: Matrix) -> Matrix:
        """
        Bias of categorical visible states.

        Large positive (negative) `z` (de)activates the state.
        """
        return self.a_A.T + H @ self.W_A.T

    def sample_x_wake(self, H: Matrix, observation: Observation) -> MatrixTriplet:
        """
        Sample x ~ p[x|h, o=(xi, e)].
        """
        xi, event = observation

        X_A = self.sample_x_wake_binary(H, observation=(xi[0], event[0]))
        X_B = self.sample_x_wake_gamma(H, observation=(xi[1], event[1]))
        X_C = self.sample_x_wake_gauss(H, observation=(xi[2], event[2]))
        return X_A, X_B, X_C

    def sample_x_wake_binary(self, H: Matrix, observation: ObservationMatrix) -> Matrix:
        """
        Sample categorical (group A) states x ~ p[x|h, o=(xi,e)].

        The mask indicates the presence (e=1) [absence (e=0)] of the value.
        """
        xi, mask = observation
        # No mask => all values observed => clamp all values.
        if mask.size == 0:
            return xi

        X = zeros_like(xi)
        # Clamp variables that are observed.
        X[mask] = xi[mask]
        # Sample missing values.
        # TODO [#44]: Generate only the visible states that we need.
        X[~mask] = self.sample_x_binary(H)[~mask]

        return X

    def sample_x_wake_gauss(self, H: Matrix, observation: ObservationMatrix) -> Matrix:
        """
        Sample numerical (group C) states x ~ p[x|h, o=(xi,e)].

        The mask indicates the presence (e=1) [absence (e=0)] of the value.
        """
        xi, mask = observation
        # No mask => all values observed => clamp all values.
        if mask.size == 0:
            return xi

        X = zeros_like(xi)
        # Clamp variables that are observed.
        X[mask] = xi[mask]
        # Sample missing values.
        # TODO [#44]: Generate only the visible states that we need.
        X[~mask] = self.sample_x_gauss(H)[~mask]

        return X

    def sample_x_wake_gamma(self, H: Matrix, observation: ObservationMatrix) -> Matrix:
        """
        Sample time-to-event (group B) states x ~ p[x|h, o=(xi, e)].

        The mask indicates whether states are censored (e=0), and xi denotes its
        censoring time.
        """
        xi, mask = observation
        # No mask => all values observed => clamp all values.
        if mask.size == 0:
            return xi

        X = zeros_like(xi)
        # Clamp variables that are observed.
        X[mask] = xi[mask]
        # Sample censored event-variables.
        ALPHA, BETA = self.alpha_beta(H)
        X[~mask] = sample_interval_truncated_gamma_distribution(
            ALPHA[~mask], BETA[~mask], xi[~mask]
        )

        return X

    def sample_x(self, H: Matrix) -> MatrixTriplet:
        """
        Sample from distribution x ~ p(x|h).
        """
        return self.sample_x_binary(H), self.sample_x_gamma(H), self.sample_x_gauss(H)

    def p_x_condition_h_binary(self, H: Matrix) -> Matrix:
        """
        Calculate visible units conditioned on hidden variables p(x=1|h).
        """
        return sigmoid(-self.z(H))

    def sample_x_binary(self, H: Matrix) -> Matrix:
        """
        Sample categorical states from the sigmoid function.

        x ~ p(x|h) where x={0, 1} belongs to group A.
        """
        # Number of records.
        m = H.shape[0]
        U = random.uniform(size=(m, self.n_categorical_units))

        # Calculate p(x=1|h).
        P = self.p_x_condition_h_binary(H)

        # Turn hidden unit on when probability is larger than random uniform number,
        X = (P > U).astype(float64)
        return X

    def sample_x_gamma(self, H: Matrix) -> Matrix:
        """
        Sample time-to-event variables from the truncated gamma distribution.

        x ~ p(x|h) where x belongs to group B, and p(x|h) is the right truncated gamma
        distribution defined on the interval [0, 1].
        """
        ALPHA, BETA = self.alpha_beta(H)
        return sample_right_truncated_gamma_distribution(ALPHA, BETA, 1.0)

    def sample_x_gauss(self, H: Matrix) -> Matrix:
        """
        Sample numerical variables from the Gaussian distribution.

        x ~ N[mu, sigma|h] where x belongs to group C, and N[] is the normal
        distribution with mean determined by the latent states h.
        """
        mu = self.mean_x_gauss(H)
        # Draw from Gaussian distribution with mean `MU` and standard deviation
        # `self.sigma`.
        return mu + random.normal(size=mu.shape, scale=abs(self.sigma).T)

    def reconstruct_mu_sigma(self, X: Matrix) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstruct mean and standard deviation based on visible states `X`.
        """
        H = self.transform(X)
        mu = self.mean_x_gauss(H)
        return mu.mean(axis=0), self.sigma.flatten()

    def has_missing_data(self, X: Matrix, ignore_censor: bool = False) -> bool:
        """
        Do the observations contain missing or censored data?
        """
        xi, event = self._unpack(X, normalise=False)
        if not ignore_censor and event.size > 0:
            if (event == 0).any():
                return True
        for x_i in xi:
            if x_i.size > 0 and isnan(x_i).any():
                return True

        return False

    def p_h_condition_x(self, xi: MatrixTriplet) -> Matrix:
        """
        Calculate latent activation probability conditioned on observations p(h=1|x).
        """
        return sigmoid(-self.phi(xi))

    def gibbs_sleep_update(self, X: MatrixTriplet) -> MatrixTriplet:
        """
        Perform a single Gibbs update step on `X`.
        """
        H = self.sample_h_sleep(X)
        return self.sample_x_sleep(H)

    def _parse_column_names(self, X: Matrix):
        """
        Init the data's column names/indices, guessing their value when absent.
        """
        if self.categorical_columns:
            self.n_categorical_units = len(self.categorical_columns)
        if self.numeric_columns:
            self.n_numeric_units = len(self.numeric_columns)
        if self.survival_columns:
            self.n_event_units = len(self.survival_columns)
        self.n_v = self.n_categorical_units + self.n_event_units + self.n_numeric_units

        if self.n_v == 0:
            raise ValueError("Missing column specification.")

    def check_X(self, X: Matrix):
        """
        Verify that input data adheres to the bounds.
        """
        xi_A = get_columns(X, self.categorical_columns)
        if xi_A.size > 0:
            distinct_categories = unique(xi_A[~isnan(xi_A)])
            if len(distinct_categories) > 2:
                # Allow floating point values for categories, but only if on the
                # unit interval.
                if any((xi_A < 0) | (xi_A > 1)):
                    raise ValueError("Categorical data not in the [0,1] interval.")
            elif not set(distinct_categories.astype(int)).issubset({0, 1}):
                raise ValueError("Categorical data not in the [0,1] interval.")

        events = get_columns(X, self.event_columns)
        if events.size > 0:
            indicators = unique(events)
            if len(indicators) > 2:
                raise ValueError(
                    f"Invalid event indicator values in columns {self.event_columns}."
                )
            elif not set(indicators.astype(int)).issubset({0, 1}):
                raise ValueError(
                    f"Indicator values (in columns {self.event_columns}) must be 0 or 1."
                )

    def fit(self, X: Matrix, y=None):
        """
        Validate model input and train model.
        """
        self.is_fitted_ = False
        self.n_hidden_units = int(self.n_hidden_units)
        self.check_X(X)
        X = X.astype(float64)

        self.weight_decay_ = self._parse_weight_decay()
        self.eps = self._parse_learning_rate()

        self._parse_column_names(X)

        # Determine time horizon.
        XI_B = get_columns(X, self.survival_columns)
        self.time_horizon_ = array([1.0 for _ in range(len(self.survival_columns))])
        if self.time_horizon is not None and XI_B.size > 0:
            if isinstance(self.time_horizon, float):
                self.time_horizon_ = XI_B.max(axis=0, keepdims=True) * self.time_horizon
            else:
                # Enlarge horizon by 1 per cent, in case the horizon coincides
                # with the largest value in the dataset that is censored.
                self.time_horizon_ = 1.01 * array(self.time_horizon).reshape(1, -1)

        # Initialise empty list for all metrics to evaluate.
        self.training_metrics_: Dict[str, list] = defaultdict(list)
        self.validation_metrics_: Dict[str, list] = defaultdict(list)

        # Set random state.
        reset_random_state(self.random_state)

        if self.survival_columns:
            # All the time points are the same when a single float is passed.
            if isinstance(self.risk_score_time_point, (float, np.ndarray)):
                self.risk_score_time_point_ = (
                    self.risk_score_time_point / self.time_horizon_.flatten()
                )
            # Calculate median survival times using Kaplan-Meier.
            elif self.risk_score_time_point == "median":
                t_median = []
                i_col = 0
                for t_col, e_col in zip(self.survival_columns, self.event_columns):
                    t = get_columns(X, [t_col]).flatten()
                    e = get_columns(X, [e_col]).flatten()
                    kmf = KaplanMeierFitter().fit(t, event_observed=e)
                    t_med = (
                        kmf.median_survival_time_ / self.time_horizon_.flatten()[i_col]
                    )
                    t_median.append(t_med)
                    i_col += 1
                self.risk_score_time_point_ = array(t_median)
            # Otherwise it is a function, calculate on training set.
            elif callable(self.risk_score_time_point):
                self.risk_score_time_point_ = self.risk_score_time_point(
                    XI_B / self.time_horizon_, axis=0
                )
            else:
                raise ValueError(
                    f"Unknown parameter risk_score_time_point={self.risk_score_time_point}."
                )

        # Initialise Gibbs chain with NaN replaced by these substitutions.
        self.initialise_nan_substitutions(X)

        self.initialise_parameters(X)

        # Try to cache expensive survival distribution computations.
        self._conditional_risk_cache = defaultdict(list)
        self._risk_cache = defaultdict(list)

        # Keep reference to the training set for, e.g., Brier score.
        self.X_train = X

        # For gradient ascent with momentum: previous update is 0.
        self.previous_update = {}
        for param_name in self.parameters:
            param = getattr(self, param_name)
            assert not any(isnan(param))
            self.previous_update[param_name] = zeros_like(param)

        # Previous state (empty), when using persistent contrastive divergence.
        self.X_previous_sleep = None
        if not self.dry_run:
            self.persistent_constrastive_divergence(X)

        self.is_fitted_ = True
        return self

    def reconstruction_error(self, X: Matrix) -> np.ndarray:
        """
        Calculate reconstruction error for current parameters.
        """
        if self.has_missing_data(X):
            raise ValueError("Reconstruction error not defined for unobserved data.")
        xi, _ = self._unpack(X)
        X_reconstruct = self.gibbs_update(xi)
        return np.ndarray(
            tuple(
                mean_squared_error(a, b) if a is not None else None
                for a, b in zip(xi, X_reconstruct)
            )
        )

    def energy_binary(
        self, X: Matrix, H: Matrix, as_matrix: bool = False
    ) -> np.ndarray:
        """
        Energy contribution of the categorical data (group A).
        """
        energy = X * self.z(H)
        if as_matrix:
            return energy
        return energy.sum(axis=1)

    def energy_gamma(self, X: Matrix, H: Matrix, as_matrix: bool = False) -> np.ndarray:
        """
        Energy contribution of the time-to-event variables (group B).

        Args:
            X (Matrix[m x n_v]): Visible states, gives 0 contribution when X is None.
            H (Matrix[m x n_h]): Hidden states.
            mask (Matrix[m x n_v]): Calculate energy terms for these individual visible
                states.
        """
        ALPHA, BETA = self.alpha_beta(H)
        # N.B. x^(a-1) exp[-bx] is zero for x=0 (since a>1).
        # For the other values, we can safely calculate ln[x].
        energy = X * BETA - log(X, out=full_like(X, -inf), where=(X != 0)) * (ALPHA - 1)
        if as_matrix:
            return energy
        return energy.sum(axis=1)

    def energy_gauss(self, X: Matrix, H: Matrix, as_matrix: bool = False) -> np.ndarray:
        """
        Energy contribution of the numerical data (group C).
        """
        # Gaussian part: (x_i - a_i)^2 / (2* sigma_i^2).
        quadratic = ((X - self.a_C.T) / self.sigma.T) ** 2 / 2
        # Linear part: x_i W_ij h_j / sigma_i.
        linear = X / self.sigma.T * (H @ self.W_C.T)
        energy = linear + quadratic
        if as_matrix:
            return energy
        return energy.sum(axis=1)

    def energy(self, X: MatrixTriplet, H: Matrix) -> np.ndarray:
        """
        Energy function of the model.

        Args:
            X=(X_A, X_B, X_C) (array[m x n_v]): Visible units.
            H (array[m x n_h]): Hidden units.

        Returns:
            array[m]: Energy for each row (X, H).
        """
        X_A, X_B, X_C = X
        # Model bias.
        E_H = (H @ self.b).flatten()
        return (
            self.energy_binary(X_A, H)
            + self.energy_gamma(X_B, H)
            + self.energy_gauss(X_C, H)
            + E_H
        )

    def mean_x(self, X: Matrix, H: Matrix) -> MatrixTriplet:
        """
        Average visible states <x>_p(x|h) given the latent states h.
        """
        xi, event = self._unpack(X)
        mean_xi = (
            self.mean_x_binary(H),
            self.mean_x_gamma(xi[1], H, event),
            self.mean_x_gauss(H),
        )
        return self._compress(mean_xi, event)

    def mean_x_binary(self, H: Matrix) -> Matrix:
        """
        Average visible visible states <x>_p(x|h) given the latent states h.
        """
        return self.p_x_condition_h_binary(H)

    def mean_x_gauss(self, H: Matrix) -> Matrix:
        """
        Average numeric states <x>_p(x|h) given the latent states h.
        """
        return self.a_C.T - H @ self.W_C.T * self.sigma.T

    def mean_x_gamma(self, XI: Matrix, H: Matrix, event: Matrix) -> Matrix:
        """
        Average visible states <x>_p(x|h, o) given the latent states h.
        """
        ALPHA, BETA = self.alpha_beta(H)
        X = zeros_like(XI)
        mask = event.astype(bool)

        # Integral dx x p(x|h) = [b^a / gamma(a,b)] integral_0^1 dx x^(a) exp(-bx) =
        # 1/b gamma(a+1, b) / gamma(a,b)
        X[mask] = normalisation_gamma_distribution(
            ALPHA[mask] + 1, BETA[mask]
        ) / normalisation_gamma_distribution(ALPHA[mask], BETA[mask])

        if X[~mask].size > 0:
            # The mean of an unobserved event should be larger, given that it is
            # observed up to xi.
            X[~mask] = normalisation_gamma_interval_distribution(
                ALPHA[~mask] + 1, BETA[~mask], XI[~mask]
            ) / normalisation_gamma_interval_distribution(
                ALPHA[~mask], BETA[~mask], XI[~mask]
            )

        return X

    def get_number_of_rows(self, X: MatrixTriplet) -> int:
        """
        Pick number of rows from first not None matrix.
        """
        m: int = next(X_i.shape[0] for X_i in X if X_i.size > 0)
        return m

    def energy_gradient(self, X: MatrixTriplet, H: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate gradient of energy w.r.t. fitting parameters, i.e. <d/dtheta E(x, h)>.
        """
        m = self.get_number_of_rows(X)
        X_A, X_B, X_C = X

        gradient = defaultdict(float)

        # Parameters categorical data (group A).
        gradient["W_A"] = X_A.T @ H / m
        gradient["a_A"] = X_A.mean(axis=0, keepdims=True).T

        # Parameteres time-to-event data (group B).
        gradient["V"] = -log(X_B).T @ H * np.sign(self.V) / m
        gradient["W_B"] = X_B.T @ H / m
        gradient["a_B"] = X_B.mean(axis=0, keepdims=True).T
        gradient["c"] = -np.sign(self.c) * log(X_B).mean(axis=0, keepdims=True).T

        # Parameters numerical data (group C).
        gradient["W_C"] = X_C.T @ H / m
        gradient["a_C"] = -X_C.mean(axis=0, keepdims=True).T
        # Gradient of sigma is decomposed in a linear and quadratic part.
        gaussian = (X_C - self.a_C.T) ** 2 / self.sigma.T ** 3
        linear = X_C * (H @ self.W_C.T) / self.sigma.T ** 2
        gradient["sigma"] = -(gaussian + linear).mean(axis=0, keepdims=True).T

        # Latent bias.
        gradient["b"] = H.mean(axis=0, keepdims=True).T
        return gradient

    def free_energy_h(self, H: Matrix) -> np.ndarray:
        """
        Calculate the configurational free energy F(h) of the latent state.

        Definition F(h):
        exp[-F(h)] = integral dx exp[-E(x,h)],
        (or sum over visible units when x is binary).

        Args:
            H (array[m x n_h]): Hidden units.

        Returns:
            array[m]: Free energy for each row.
        """
        # Binary harmonium: sum_i log sigmoid(z_i)
        F_A = -logaddexp(0, -self.z(H)).sum(axis=1)

        # Gamma harmonium: -ln [Gamma(a) gamma*(a,b)].
        ALPHA, BETA = self.alpha_beta(H)
        F_B = -log_normalisation_gamma_distribution(ALPHA, BETA).sum(axis=1)

        # Gaussian harmonium: <a/sigma|wh> - 1/2|Wh|^2 - ln[2pi sigma^2].
        F_C = (
            # sum_{ij} a_i W_ij h_j / sigma_i.
            (H @ self.W_C.T @ (self.a_C / self.sigma)).flatten()
            # sum_i (sum_j W_ij h_j)^2 / 2.
            - ((H @ self.W_C.T) ** 2 / 2).sum(axis=1)
            # sum_i 1/2 ln[2 pi sigma_i^2].
            - (1 / 2 * log(2 * pi * self.sigma ** 2)).sum(axis=0)
        )

        F_H = (H @ self.b).flatten()

        return F_A + F_B + F_C + F_H

    def _inflate(self, X: Matrix) -> Tuple[MatrixTriplet, MatrixTriplet]:
        """
        Unpack and inflate variables and events in triplets.
        """
        (xi_A, xi_B, xi_C), event_B = self._unpack(X, verify=False)
        event_A = event_C = array([], dtype=bool_)

        nan_A = isnan(xi_A, order="C", dtype=bool_)
        nan_C = isnan(xi_C, order="C", dtype=bool_)
        # Use the column indices [i.e., where(mask)[1]] to pick the
        # corresponding fillers.
        if nan_A.any():
            fillers_A = get_columns(self.fill_nan_, self.categorical_columns)
            xi_A[nan_A] = take(fillers_A, where(nan_A)[1])
            event_A = ~nan_A
        if nan_C.any():
            fillers_C = get_columns(self.fill_nan_, self.numeric_columns)
            xi_C[nan_C] = take(fillers_C, where(nan_C)[1])
            event_C = ~nan_C

        # For the time-to-event variables (group B), replace nan->0.
        # This ensures that `sample_x_wake` generates samples from
        # the entire [0,1] interval (instead of [xi, 1]).
        xi_B[isnan(xi_B)] = 0.0
        return ((xi_A, xi_B, xi_C), (event_A, event_B, event_C))

    def inflate_event_masks(
        self, X: MatrixTriplet, event: Matrix = array([])
    ) -> MatrixTriplet:
        """
        Extract event masks of group A and C data by looking for missing values.
        """
        m = self.get_number_of_rows(X)
        empty_shape = (m, 0)
        event_binary = event_gamma = event_gauss = array([], dtype=bool_).reshape(
            empty_shape
        )
        if X[0].size > 0 and isnan(X[0]).any():
            event_binary = (~isnan(X[0], order="C")).astype(bool_)
        if X[2].size > 0 and isnan(X[2]).any():
            event_gauss = (~isnan(X[2], order="C")).astype(bool_)
        if event.size > 0:
            event_gamma = event.astype(bool_)
        return (
            event_binary,
            event_gamma,
            event_gauss,
        )

    def _partition_function_i(
        self, x_args, x_A, x_B, x_C, mask_A, mask_B, mask_C
    ) -> float:
        """
        Compute latent partition function of a row.
        """
        # The first n_B elements in `x_args` are survival variables, and the
        # remaining elements (n_C in total) are Gaussian variables.
        x_args = array(x_args, order="C")

        # Verify memory layout of all trainable parameters.
        parameter_arrays = tuple(self.get_parameters().values())
        check_arrays(*parameter_arrays)
        check_arrays(x_args, x_A, x_B, x_C)
        check_arrays(mask_A, mask_B, mask_C, dtype=bool_)

        return _partition_function_i(
            x_args,
            x_A,
            x_B,
            x_C,
            mask_A,
            mask_B,
            mask_C,
            self.a_A,
            self.a_B,
            self.a_C,
            self.c,
            self.W_A,
            self.W_B,
            self.W_C,
            self.V,
            self.sigma,
            self.b,
        )

    def _lambda_partition_function_i(self, x_A, x_B, x_C, mask_A, mask_B, mask_C):
        """
        Produce SciPy `LowLevelCallable` version of _partition_function_i.
        """
        # Verify memory layout of all trainable parameters.
        parameter_arrays = tuple(self.get_parameters().values())
        check_arrays(*parameter_arrays)
        check_arrays(x_A, x_B, x_C)
        check_arrays(mask_A, mask_B, mask_C, dtype=bool_)

        return _lambda_partition_function_i(
            x_A,
            x_B,
            x_C,
            mask_A,
            mask_B,
            mask_C,
            self.a_A,
            self.a_B,
            self.a_C,
            self.c,
            self.W_A,
            self.W_B,
            self.W_C,
            self.V,
            self.sigma,
            self.b,
        )

    def _hidden_state_partition_function_integral(self, xi, mask):
        r"""
        Calculate the partition function Z(o) over the latent states.

        Z(o) \equiv e^{-\mathcal{F}(o)}
            = \sum_h \int \mathrm{d}x e^{-E(x, h)} \chi(x, o),

        Compute Z(o) by:
        1) first summing over all latent states analytically,
        2) subsequently carry out the integration w.r.t. x using numerical
            integration.
        """
        X_A, X_B, X_C = xi
        mask_A, mask_B, mask_C = self.inflate_event_masks(xi, mask)

        m = self.get_number_of_rows(xi)
        Z = zeros(m)
        for k in range(m):
            # Copy, because we perform inplace assignments.
            x_A = copy(X_A[k].astype(float64), order="C")
            x_B = copy(X_B[k].astype(float64), order="C")
            x_C = copy(X_C[k].astype(float64), order="C")

            event_A = ascontiguousarray(mask_A[k])
            event_B = ascontiguousarray(mask_B[k])
            event_C = ascontiguousarray(mask_C[k])

            # No numerical integration is necessary.
            if sum(~event_B) + sum(~event_C) == 0:
                Z[k] = self._partition_function_i(
                    tuple(), x_A, x_B, x_C, event_A, event_B, event_C
                )
                continue

            # Integrate survival variables from censor time to 1.
            boundaries_B = column_stack([x_B[~event_B], ones_like(x_B[~event_B])])
            # Integrate numerical variables from -inf to inf.
            inf_array = full_like(x_C[~event_C], inf)
            boundaries_C = column_stack([-inf_array, inf_array])
            boundaries = append(boundaries_B, boundaries_C).reshape(-1, 2)

            integral_function = self._lambda_partition_function_i(
                x_A,
                x_B,
                x_C,
                event_A,
                event_B,
                event_C,
            )
            value, _ = nquad(integral_function, boundaries)
            Z[k] = value
        return Z

    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(x) = - ln( sum_h exp[-E(x,h)]).
        """
        if self.has_missing_data(X):
            return self.modified_free_energy_x(X)

        xi, event = self._unpack(X)
        X_A, X_B, X_C = xi
        F = -logaddexp(0, -self.phi(xi)).sum(axis=1)

        F += (X_A @ self.a_A).flatten()
        F += (X_B @ self.a_B - log(X_B) @ abs(self.c)).flatten()
        quadratic = ((X_C - self.a_C.T) / self.sigma.T) ** 2 / 2
        F += quadratic.sum(axis=1)

        return F

    def _proba(
        self,
        X: MatrixTriplet,
        event: Matrix,
        indices: Union[list, int],
        survival_distribution: bool = True,
    ) -> np.ndarray:
        r"""
        Discriminative joint distribution p(xi_i|o_{-i}, e) of events.

        Args:
            indices: Set of survival variable indices \{\xi\}_i to evaluate
                the joint distribution.

        Returns: For each record, the conditional distribution per event
            variable in the set `indices`

        Evaluates:
        - p(\xi_i | o_{-i}) when `survival_distribution` is
          False.
        - S(\xi_i | o_{-i} ) when `survival_distribution` is True.
        """
        if isinstance(indices, int):
            indices = [indices]

        # Calculate: exp[-F(o)] / integral d{x_B}^i exp[-F(o)] where the
        # integral is over the entire set.
        # 1)
        # Numerator: exp[-F(o)].
        mask_numerator = event.copy()
        if isinstance(survival_distribution, bool):
            mask_numerator[:, indices] = 1.0 - float(survival_distribution)
        # Assume it is a censor mask, when `survival_distribution` is a matrix,
        # specifying per variable whether to compute a survival distrubution.
        elif isinstance(survival_distribution, np.ndarray):
            mask_numerator[:, indices] = survival_distribution
        else:
            raise ValueError("survival_distribution neither a bool nor a mask.")

        Z_o = self._hidden_state_partition_function(X, mask_numerator)

        # 2)
        # Denominator: Z(x_{-i}) = integral d{x^B}_i exp[-F(o)] =>
        # set o^i_B = (0, 0) for each i in the set.
        mask_denominator = event.copy()
        xi_B = X[1].copy()
        mask_denominator[:, indices] = 0.0
        xi_B[:, indices] = 0.0

        Z = self._hidden_state_partition_function((X[0], xi_B, X[2]), mask_denominator)

        # Carefully divide by Z, in case it is zero.
        with np.errstate(all="raise"):
            try:
                S = Z_o / Z
            except FloatingPointError:
                S = np.where(Z_o != 0, Z_o, 0.0)
        return S

    def _proba_singletons(
        self,
        X: Matrix,
        survival_distribution: bool = True,
    ) -> Matrix:
        r"""
        Discriminative distribution per event variable x_i.

        For each i, evaluate:
        - p(x_i | o_{-i}) when `survival_distribution` is False.
        - S(x_i | o_{-i}) when `survival_distribution` is True.
        """
        # Don't impose the x > 0 boundary condition when we are interested in
        # the survival distribution.
        xi, event = self._unpack(X, verify=(not survival_distribution))

        if event.size == 0:
            event = ones_like(xi[1], dtype=bool_)

        distributions = [
            self._proba(xi, event, i, survival_distribution)
            for i in range(self.n_event_units)
        ]
        return column_stack(distributions)

    def predict_proba(self, X: Matrix, survival_distribution: bool = True) -> Matrix:
        r"""
        Discriminative distribution per event variable.

        For each i, evaluate:
        - p(x_i = \xi_i | o_{-i}) when `survival_distribution` is False.
        - p(x_i > \xi_i | o_{-i}) when `survival_distribution` is True.
        (N.B. the evaluation points are determined by te values in `X` )
        """
        check_is_fitted(self, "is_parameters_initialised_")
        return self._proba_singletons(X, survival_distribution)

    def _clean_time_point(self, time_point) -> dict:
        """
        Interpret time point as dict.

        None means: use risk_score_time_point_.
        """

        def unnormalised_time(column):
            """Compute unnormalised risk_score_time_point time."""
            i = self.survival_columns.index(column)
            return self.risk_score_time_point_[i] * self.time_horizon_.flatten()[i]

        # Key is column name, value is `t_i`.
        time_point_dict = {}
        if time_point is None:
            # Compute only for first time-to-event variable.
            column = self.survival_columns[0]
            time_point_dict = {column: unnormalised_time(column)}
        elif isinstance(time_point, float):
            time_point_dict = {self.survival_columns[0]: time_point}
        elif isinstance(time_point, dict):
            time_point_dict = time_point
        elif isinstance(time_point, np.ndarray):
            time_point_dict = {
                column: time_point[i] for i, column in enumerate(self.survival_columns)
            }
        elif time_point in self.survival_columns:
            time_point_dict = {time_point: unnormalised_time(time_point)}
        elif time_point == "all":
            time_point_dict = {c: unnormalised_time(c) for c in self.survival_columns}
        else:
            raise ValueError("Illegal value for argument `time_point`.")
        return time_point_dict

    def predict(
        self,
        X: Matrix,
        conditional_probability: bool = False,
        time_point: Optional[Union[dict, np.ndarray, str]] = None,
    ) -> pd.DataFrame:
        r"""
        Discriminative survival S(x_i=t_i|o_{-i}) distribution.

        The survival is evaluated at time t_i (`time_point`). Higher probability
        means longer survival, and less risk.

        Args:
            conditional_probability (bool): Whether to condition on:
                - True: All variables except the target variable, i.e.,
                    on $o_{-i}$.
                - False: Only the time-independent variables, i.e., marginalise
                    out the other survival variables.

            time_point (dict): A dict of survival variables and corresponding time
                points to compute the survival distribution.
                - When `None` compute, _only_ the first time-to-event variable
                at (unnormalised) `risk_score_time_point_` (median by default).
                - When "all", compute distribution for each time-to-event
                variable individually, using `risk_score_time_point_` (median
                by default).
        """
        check_is_fitted(self, "is_parameters_initialised_")

        # Compute the survival distribution only the variables specified using
        # time point.
        time_point_dict = self._clean_time_point(time_point)

        survival_probability = {}
        for column_i, t_i in time_point_dict.items():
            i = self.survival_columns.index(column_i)
            tau = t_i / self.time_horizon_.flatten()[i]
            if not conditional_probability:
                predicted_risk = self._risk_i(X, i, time_point=tau)
            else:
                predicted_risk = self._conditional_risk_i(X, i, time_point=tau)
            survival_probability[column_i] = predicted_risk

        return pd.DataFrame(survival_probability)

    def predict_joint_proba(self, X: Matrix) -> np.ndarray:
        r"""
        Discriminative joint event distribution p(xi^B|xi_{-B}, e).

        Predicts the probability of all event times combined.
        """
        check_is_fitted(self, "is_parameters_initialised_")

        xi, event = self._unpack(X)

        if xi[1].size == 0:
            raise ValueError("No time-to-event variables specified for scoring.")

        return self._proba(
            xi,
            event,
            indices=list(range(self.n_event_units)),
            survival_distribution=event,
        )

    def score(
        self,
        X: Matrix,
        y=None,
        conditional_probability: bool = False,
        time_point: Optional[Union[dict, np.ndarray, str]] = None,
    ) -> Union[float, dict]:
        """
        Concordance index for time-to-event variables.

        Args:
            conditional_probability (bool): Whether to condition on:
                - True: All variables except the target variable, i.e.,
                    on $o_{-i}$.
                - False: Only the time-independent variables, i.e., marginalise
                    out the other survival variables.

            time_point (dict): A dict of survival variables and corresponding
                time points to compute the risk score (via the survival
                distribution).
                - When `None` compute, _only_ the first time-to-event variable
                at (unnormalised) `risk_score_time_point_` (median by default).
                - When "all", compute distribution for each time-to-event
                variable individually, using `risk_score_time_point_` (median
                by default).
        """
        return self.concordance_index(X, conditional_probability, time_point=time_point)

    def brier_loss(
        self,
        X: Matrix,
        conditional_probability: bool = False,
        time_point: Optional[Union[dict, np.ndarray, str]] = None,
    ) -> Union[float, dict]:
        """
        Compute Brier loss for time-to-event variables.

        Args:
            conditional_probability (bool): Whether to condition on:
                - True: All variables except the target variable, i.e.,
                    on $o_{-i}$.
                - False: Only the time-independent variables, i.e., marginalise
                    out the other survival variables.

            time_point (dict): A dict of survival variables and corresponding
                time points to compute the survival distribution.
                - When `None` compute, _only_ the first time-to-event variable
                at (unnormalised) `risk_score_time_point_` (median by default).
                - When "all", compute distribution for each time-to-event
                variable individually, using `risk_score_time_point_` (median
                by default).
        """
        time_point = self._clean_time_point(time_point)
        predicted_risk = self.predict(X, conditional_probability, time_point=time_point)

        brier_scores = {}
        for time_column, tau in time_point.items():
            i = self.survival_columns.index(time_column)
            event_column = self.event_columns[i]
            brier_i = brier_loss(
                train_time=get_columns(self.X_train, time_column),
                train_event=get_columns(self.X_train, event_column),
                test_time=get_columns(X, time_column),
                test_event=get_columns(X, event_column),
                S_pred=predicted_risk[time_column].to_numpy(),
                tau=tau,
            )
            brier_scores[time_column] = brier_i

        if len(brier_scores) == 1:
            return brier_scores.popitem()[1]

        return brier_scores

    def bayesian_information_criterion(self, X: Matrix, negate: bool = False):
        """
        Bayesian information criterion for censored data.
        """
        likelihood = exp(self.log_likelihood(X).sum())
        event = get_columns(X, self.event_columns, dtype=bool_)
        # Instead of number of samples, we use the number of events that are
        # completely observed.
        d = (event.sum(axis=1) == self.n_event_units).sum()
        # Number of free parameters.
        k = (
            self.W_A.size
            + self.a_A.size
            + self.W_B.size
            + self.V.size
            + self.a_B.size
            + self.c.size
            + self.W_C.size
            + self.a_C.size
            + self.sigma.size
            + self.b.size
        )
        sgn = 1
        if negate:
            sgn = -1
        return sgn * (k * log(d) - 2 * likelihood)

    def concordance_index(
        self,
        X: Matrix,
        conditional_probability: bool = False,
        time_point: Optional[Union[dict, np.ndarray, str]] = None,
    ) -> Union[float, dict]:
        """
        Concordance index for time-to-event variables.

        Args:
            conditional_probability (bool): Whether to condition on:
                - True: All variables except the target variable, i.e.,
                    on $o_{-i}$.
                - False: Only the time-independent variables, i.e., marginalise
                    out the other survival variables.

            time_point (dict): A dict of survival variables and corresponding
                time points to compute the risk scores (via the survival
                distribution).
                - When `None` compute, _only_ the first time-to-event variable
                at (unnormalised) `risk_score_time_point_` (median by default).
                - When "all", compute distribution for each time-to-event
                variable individually, using `risk_score_time_point_` (median
                by default).
        """
        check_is_fitted(self, "is_parameters_initialised_")

        (_, X_B, _), event = self._unpack(X)
        if X_B.size == 0:
            raise ValueError("No time-to-event variables specified for scoring.")

        time_point = self._clean_time_point(time_point)
        predicted_risk = self.predict(X, conditional_probability, time_point)

        concordance_indices = {}
        for column_name in time_point.keys():
            t_index = self.survival_columns.index(column_name)
            c_i = concordance_index(
                event_times=X_B[:, t_index],
                predicted_scores=predicted_risk[column_name],
                event_observed=event[:, t_index],
            )
            concordance_indices[column_name] = c_i

        if len(concordance_indices) == 1:
            return concordance_indices.popitem()[1]

        return concordance_indices

    def conditional_score(
        self,
        X: Matrix,
        y=None,
        time_point: Optional[Union[dict, np.ndarray, str]] = None,
    ) -> Union[float, dict]:
        """
        C-index for time-to-event variable, conditioned on all other variables.

        Predict using all variables (also time-to-event variables) except the
        target variable.
        """
        return self.score(X, y, conditional_probability=True, time_point=time_point)

    def _conditional_risk_i(
        self, X: Matrix, i: int, time_point: Optional[float] = None
    ):
        r"""
        Risk score of `i`th survival variable, conditioned on all other values.

        The risk score is defined as the survival distribution at a fixed point
        \tau_i, conditioned on all observations except the target variable i
        (o_{-i}):

        S(x_i^B=\tau_i|o_{-i}) \equiv p(x_i^B > \tau_i|o_{-i}),

        where \tau_i refers to `time_point` or, when left unspecified, to
        `risk_score_time_point_` (e.g., the median value).
        """
        if time_point is None:
            time_point = self.risk_score_time_point_[i]

        # Try to look up computation result in cache.
        X_hash = hash_array(X)
        if (
            getattr(self, "is_fitted_", False)
            and X_hash in self._conditional_risk_cache
        ):
            for cache_i in self._conditional_risk_cache[X_hash]:
                if cache_i["i"] == i and cache_i["time_point"] == time_point:
                    return cache_i["value"]

        (X_A, X_B, X_C), event = self._unpack(X)

        # The conditional survival distribution, evaluated at a specific
        # time (e.g., 0.5 or median), is used as a proxy for the risk.
        X_B_prime = X_B.copy()
        X_B_prime[:, i] = time_point
        result = self._proba(
            (X_A, X_B_prime, X_C), event, indices=i, survival_distribution=True
        )

        # Store computation in cache when training finished.
        if getattr(self, "is_fitted_", False):
            self._conditional_risk_cache[X_hash].append(
                {"i": i, "time_point": time_point, "value": result}
            )
        return result

    def _risk_i(self, X: Matrix, i: int, time_point: Optional[float] = None):
        r"""
        Risk of `i`th survival variable, conditioned on time-indep. values.

        The risk score is defined as the survival distribution at a fixed point
        \tau_i conditioned on all observations with the survival variables
        removed:

        S(x_i^B=\tau_i|o \setminus x^B)
            \equiv p(x_i^B > \tau_i|o \setminus x^B),

        where \tau_i refers to `time_point` or, when left unspecified, to
        `risk_score_time_point_` (e.g., the median value).
        """
        if time_point is None:
            time_point = self.risk_score_time_point_[i]

        # Try to look up computation result in cache.
        X_hash = hash_array(X)
        if getattr(self, "is_fitted_", False) and X_hash in self._risk_cache:
            for cache_i in self._risk_cache[X_hash]:
                if cache_i["i"] == i and cache_i["time_point"] == time_point:
                    return cache_i["value"]

        (X_A, X_B, X_C), _ = self._unpack(X)

        # Censor all survival variables (except target variable) at 0, ensuring
        # that the variables are completely marginalised out.
        X_B_prime = zeros_like(X_B)
        X_B_prime[:, i] = time_point
        event_prime = zeros_like(X_B, dtype=bool)
        result = self._proba(
            (X_A, X_B_prime, X_C), event_prime, indices=i, survival_distribution=True
        )

        # Store computation in cache when training finished.
        if getattr(self, "is_fitted_", False):
            self._risk_cache[X_hash].append(
                {"i": i, "time_point": time_point, "value": result}
            )
        return result

    def modified_free_energy_x(self, X: Matrix) -> np.ndarray:
        r"""
        Modified free energy F(o) in presence (partially) unobserved data.

        That is, calculate F(o) where
        e^{-\mathcal{F}(o)} = \sum_h \int \mathrm{d}x e^{-E(x, h)} \chi(x, o),

        We use a modified definition that directly links to the likelihood:
        exp[-F(o)] = sum_h integral dx exp[-E(x,h)] g(x,o).
        so that
        likelihood(o) = integral dx p(x) g(x, o) = -F(o) - ln Z
        """
        xi, event = self._unpack(X)
        return -np.log(self._hidden_state_partition_function(xi, event))

    def _hidden_state_partition_function(
        self, xi: MatrixTriplet, event: Optional[Matrix] = None
    ) -> np.ndarray:
        """
        Choose computation method depending on number of states.
        """
        if self.n_hidden_units >= 10:
            return self._hidden_state_partition_function_integral(xi, event)
        return self._hidden_state_partition_function_sum(xi, event)

    def _hidden_state_partition_function_sum(
        self, X: MatrixTriplet, event: Optional[Matrix] = None
    ) -> np.ndarray:
        r"""
        Calculate the partition function Z(o) over the latent states.

        Z(o) \equiv e^{-\mathcal{F}(o)}
            = \sum_h \int \mathrm{d}x e^{-E(x, h)} \chi(x, o),

        Compute Z(o) by:
        1) first evaluating integral w.r.t. x using analytical expression and
        2) subsequently summing over all latent configurations.
        """
        event_A, event_B, event_C = self.inflate_event_masks(X, event)
        X_A, X_B, X_C = X

        if any(X_B > 1) or any(X_B < 0):
            raise ValueError(
                "Time-to-event variables out of [0,1] range. "
                "Perhaps `event_scale_factor` is too low?"
            )

        m = self.get_number_of_rows(X)
        Z = zeros(m)
        # We can no longer carry out the summation
        # sum_h exp[-E(x,h)]
        # analytically, so we have to resort to numerical computation over all states.
        for h in generate_binary_permutations(self.n_hidden_units):
            # Do the sum over `h` for all `m` records in X. => Repeat `h` m times.
            H = h.reshape(1, -1).repeat(m, axis=0)
            # Compute product as log sums for numerical stability.
            log_sum = self.log_energy_factor_binary(X_A, H, event_A)
            log_sum += self.log_energy_factor_gamma(X_B, H, event_B)
            log_sum += self.log_energy_factor_gauss(X_C, H, event_C)
            log_sum += (-H @ self.b).flatten()
            total_product = exp(log_sum)
            if np.any(total_product < 0):
                raise ValueError
            Z += total_product
        return Z

    def log_energy_factor_binary(
        self, X: Matrix, H: Matrix, mask: Matrix
    ) -> np.ndarray:
        """
        Missing data corrected energy contribution of the categoric variables (group A).
        """
        if mask.size == 0:
            return -self.energy_binary(X, H)

        p = zeros_like(X)
        z = self.z(H)
        # Observed values.
        p[mask] = -(X * z)[mask]
        # Marginalise out missing values.
        p[~mask] = logaddexp(-z[~mask], 0)
        return p.sum(axis=1)

    def energy_factor_binary(self, X: Matrix, H: Matrix, mask: Matrix) -> np.ndarray:
        """
        Missing data corrected energy contribution of the categoric variables (group A).
        """
        if mask.size == 0:
            return exp(-self.energy_binary(X, H))

        p = zeros_like(X)
        z = self.z(H)
        # Observed values.
        p[mask] = exp(-(X * z)[mask])
        # Marginalise out missing values.
        p[~mask] = 1 + exp(-z[~mask])
        return p.prod(axis=1)

    def log_energy_factor_gauss(self, X: Matrix, H: Matrix, mask: Matrix) -> np.ndarray:
        """
        Missing data corrected energy contribution of the numeric variables (group C).
        """
        if mask.size == 0:
            return -self.energy_gauss(X, H)

        p = zeros_like(X)
        # 1)
        # Observed variables.
        energy = self.energy_gauss(X, H, as_matrix=True)
        p[mask] = -energy[mask]

        # 2)
        # Missing values are integrated out.
        linear = self.a_C.T / self.sigma.T * (H @ self.W_C.T)
        quadratic = -((H @ self.W_C.T) ** 2) / 2
        phase = linear + quadratic
        p[~mask] = (0.5 * log(2 * pi * self.sigma ** 2).flatten() - phase)[~mask]

        return p.sum(axis=1)

    def energy_factor_gauss(self, X: Matrix, H: Matrix, mask: Matrix) -> np.ndarray:
        """
        Missing data corrected energy contribution of the numeric variables (group C).
        """
        if mask.size == 0:
            return exp(-self.energy_gauss(X, H))

        p = zeros_like(X)
        # 1)
        # Observed variables.
        energy = self.energy_gauss(X, H, as_matrix=True)
        p[mask] = exp(-energy[mask])

        # 2)
        # Missing values are integrated out.
        linear = self.a_C.T / self.sigma.T * (H @ self.W_C.T)
        quadratic = -((H @ self.W_C.T) ** 2) / 2
        phase = linear + quadratic
        p[~mask] = (sqrt(2 * pi * self.sigma ** 2).flatten() * exp(-phase))[~mask]

        return p.prod(axis=1)

    def energy_factor_gamma(self, X: Matrix, H: Matrix, mask: Matrix) -> np.ndarray:
        r"""
        Censor corrected energy factor of the time-to-event variables (group B).

        Calculates:
        \exp[-\tilde{E}_B(o, h)] = \int dx^B \exp[-E_B(x^B, h)] \chi(x^B, o^B)
        """
        if mask.size == 0:
            return exp(-self.energy_gamma(X, H))

        p = zeros_like(X)
        # 1)
        # Observed values.
        energy = self.energy_gamma(X, H, as_matrix=True)
        p[mask] = exp(-energy[mask])
        # 2)
        # For censored values, integrate out the unobserved region (the interval
        # from censor time to 1).
        alpha, beta = self.alpha_beta(H)
        p[~mask] = normalisation_gamma_interval_distribution(
            alpha[~mask], beta[~mask], t_left=X[~mask], t_right=1.0
        )

        return p.prod(axis=1)

    def log_energy_factor_gamma(self, X: Matrix, H: Matrix, mask: Matrix) -> np.ndarray:
        r"""
        Censor corrected energy factor of the time-to-event variables (group B).

        Calculates:
        -\tilde{E}_B(o, h) = log[\int dx^B \exp[-E_B(x^B, h)] \chi(x^B, o^B)]
        """
        if mask.size == 0:
            return -self.energy_gamma(X, H)

        p = zeros_like(X)
        # 1)
        # Observed values.
        energy = self.energy_gamma(X, H, as_matrix=True)
        p[mask] = -energy[mask]
        # 2)
        # For censored values, integrate out the unobserved region (the interval
        # from censor time to 1).
        alpha, beta = self.alpha_beta(H)
        p_surv = normalisation_gamma_interval_distribution(
            alpha[~mask], beta[~mask], t_left=X[~mask], t_right=1.0
        )
        p[~mask] = log(p_surv, out=full_like(p_surv, -inf), where=(p_surv != 0))

        return p.sum(axis=1)
