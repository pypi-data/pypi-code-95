from abc import ABC, abstractmethod
from collections import defaultdict
import re
from typing import Dict, Optional, Tuple, Union

import numpy as np
from numpy import array, float64, zeros, zeros_like
import pandas as pd
from scipy.special import expit as sigmoid
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error

from harmoniums.const import Matrix, MatrixOrTriplet, MatrixTriplet, Observation
from harmoniums.utils import (
    generate_binary_permutations,
    get_columns,
    reset_random_state,
    MiniBatchIterator,
)


class BaseHarmonium(BaseEstimator, ABC):
    """
    Harmonium non-specific methods, for which the latent states are binary (h={0,1}).

    Refs:
    [1]: T. Tieleman. "Training restricted boltzmann machines using approximations to
    the likelihood gradient." In Proceedings of the 25th international conference on
    Machine learning, pages 1064–1071. ACM, 2008.
    [2]: C. Robert, Machine Learning:  A Probabilistic Perspective, 2014.
    """

    @property
    @abstractmethod
    def parameters(self) -> Tuple[str, ...]:
        """
        Free parameters of the model that can be fit.

        Array containing the variable names --- referencing a numpy array in this class
        --- of the model's free (fitting) parameters. E.g., interaction term `W`, or
        bias `a` and `b`.
        """

    def get_parameters(self) -> dict:
        """
        Get the values of the free parameters.
        """
        return {param: getattr(self, param, None) for param in self.parameters}

    def set_parameters(self, values: dict):
        """
        Set free parameter values by name.
        """
        for name, value in values.items():
            if name not in self.parameters:
                raise KeyError(
                    f"Parameter {name} is not a free parameter of this model."
                )
            setattr(self, name, value)

    @property
    @abstractmethod
    def no_penalty(self) -> Tuple[str, ...]:
        """
        Free parameters that don't get a weight decay (L2) penalty by default.

        This property is only useful when `weight_decay` != 0.
        """

    # Uninitialised value.
    iteration_step: int = -1

    def __init__(
        self,
        n_hidden_units: int,
        # When -1, determine number of units from the data.
        n_visible_units: int = -1,
        # Scale of weights is ~ 1e-2, the learning rate is a factor 1e-3 smaller than
        # that [1].
        learning_rate: Union[float, tuple, list, dict] = 1e-5,
        # Use this much from the previous update.
        momentum_fraction: float = 0.0,
        weight_decay: float = 0.0,
        random_state: int = 1234,
        CD_steps: int = 1,
        mini_batch_size: int = 50,
        n_epochs: int = 10,
        log_every_n_iterations: Optional[int] = 25,
        maximum_iteration: int = -1,
        tolerance: float = 1.0e-12,
        persistent: bool = False,
        verbose: bool = False,
        # Metrics to calculate during training.
        metrics: Tuple[str, ...] = ("reconstruction_error", "free_energy_x"),
        # Validation data for which to calculate the metrics.
        X_validation: Optional[Matrix] = None,
        # Initialise parameters by calling `fit`, but don't run constrative divergence.
        dry_run: bool = False,
        visible_columns=[],
        event_columns=[],
    ):
        self.n_hidden_units = n_hidden_units
        self.n_visible_units = n_visible_units
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
        self.learning_rate = learning_rate
        self.visible_columns = visible_columns
        self.event_columns = event_columns

        # Initialise empty list for all metrics to evaluate.
        self.metrics = metrics
        self.X_validation = X_validation

        # Set random state.
        reset_random_state(random_state)

        self.is_parameters_initialised_ = False
        # Previous state (empty), when using persistent contrastive divergence.
        self.X_previous = None

    def has_missing_data(self, X: Matrix) -> bool:
        """
        Are any of the censor indicators 0?
        """
        _, event = self._unpack(X)
        if event is not None and (event == 0).any():
            return True
        return False

    def _unpack_settings(self, param_settings) -> tuple:
        """
        Unpack parameter specific settings as a `self.parameters` like tuple.
        """
        if isinstance(param_settings, dict):
            return tuple(param_settings[k] for k in self.parameters)
        elif isinstance(param_settings, (list, tuple)) and len(param_settings) == len(
            self.parameters
        ):
            return tuple(param_settings)
        else:
            raise TypeError

    def _parse_learning_rate(self) -> tuple:
        """
        Unpack learning rate as parameter specific rate.
        """
        if isinstance(self.learning_rate, float):
            learning_rate = tuple(self.learning_rate for _ in self.parameters)
        else:
            try:
                learning_rate = self._unpack_settings(self.learning_rate)
            except TypeError:
                raise ValueError("Incorrect learning rate setting.")
        return learning_rate

    def _parse_weight_decay(self) -> tuple:
        """
        Unpack weight decay as parameter specific penalty.
        """
        if isinstance(self.weight_decay, float):
            # Don't apply weight decay to bias parameters (see Hinton RBM tutorial).
            weight_decay = tuple(
                self.weight_decay if param not in self.no_penalty else 0.0
                for param in self.parameters
            )
        else:
            try:
                weight_decay = self._unpack_settings(self.weight_decay)
            except TypeError:
                raise ValueError("Incorrect weight decay setting.")
        return weight_decay

    def _copy(self, X):
        """Return a copy if `x` is not None."""
        if X is None:
            raise ValueError("None in _copy")
            return None

        if isinstance(X, tuple):
            return self._copy_triplet(X)
        return X.copy()

    def _copy_triplet(self, X: MatrixTriplet) -> MatrixTriplet:
        """
        Make a copy of the triplet of matrices.
        """
        return (self._copy(X[0]), self._copy(X[1]), self._copy(X[2]))

    def _set_columns(self, X: Matrix, X_values: Matrix, columns: list) -> Matrix:
        """
        Set specific values of matrix.
        """
        if columns:
            if isinstance(X, pd.DataFrame):
                column_assignments = {c: X_values[:, i] for i, c in enumerate(columns)}
                X = X.assign(**column_assignments)
            else:
                X[:, columns] = X_values
        return X

    def _parse_column_names(self, X: Matrix):
        """
        Init the data's column names/indices, guessing their value when absent.
        """
        if self.visible_columns:
            self.n_visible_units = len(self.visible_columns)
            self.visible_columns_ = self.visible_columns
        # Determine the columns.
        elif not self.event_columns:
            self.n_visible_units = X.shape[1]
            if isinstance(X, pd.DataFrame):
                self.visible_columns_ = X.columns
            else:
                self.visible_columns_ = list(range(self.n_visible_units))
        else:
            raise ValueError("Unable to determine the column indices of the data.")

    def fit(self, X: Matrix, y=None):
        """
        Determine number of visible units from the data.
        """
        self._parse_column_names(X)

        # Input validation.
        self.weight_decay_ = self._parse_weight_decay()
        self.eps = self._parse_learning_rate()

        self.training_metrics_: Dict[str, list] = defaultdict(list)
        self.validation_metrics_: Dict[str, list] = defaultdict(list)

        self.initialise_parameters(X)

        # For gradient ascent with momentum: previous update is 0.
        self.X_previous_sleep = None
        self.previous_update = {
            k: zeros_like(getattr(self, k)) for k in self.parameters
        }

        if not self.dry_run:
            self.persistent_constrastive_divergence(X)

        return self

    def pseudo_log_likelihood(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the pseudo-log-likelihood sum_i ln P(x_i | x_{j!=i}).
        """
        likelihood = zeros(X.shape[0])
        # Calculate the pseudo-likelihood for each column.
        for i in range(X.shape[1]):
            P_i = self.pseudo_likelihood(X, i)
            # Take log of P(x_i | x_{j!=i}).
            likelihood += np.log(P_i)

        return likelihood

    def _sample_single_record(self, x: np.ndarray, s: int) -> np.ndarray:
        """
        Calculate sampled log pseudo likelihood for a single record.
        """
        # Number of features.
        n = x.shape[1]

        likelihood = np.zeros(shape=(x.shape[0], 1))
        # Calculate the pseudo-likelihood for each column.
        for i in np.random.choice(np.arange(n), size=s, replace=False):
            P_i = self.pseudo_likelihood(x, i)
            # Take log of P(x_i | x_{j!=i}).
            likelihood += np.log(P_i)

        # n * E[ln P(x_i)] ~= ln PL(x). Divide by `s` to average contributions.
        return n / s * likelihood

    def reconstruction_error(self, X_data: np.ndarray) -> np.ndarray:
        """
        Calculate reconstruction error for current parameters.
        """
        X_reconstruct = self.gibbs_update(X_data)
        return mean_squared_error(X_data, X_reconstruct)

    def stochastic_log_likelihood(self, X: np.ndarray, s: int) -> np.ndarray:
        """
        Approximate the pseudo-log-likelihood by summing over subset of variables
        (instead of all).
        """
        L = []
        # Go through all records.
        for i in range(X.shape[0]):
            L_i = self._sample_single_record(X[i : i + 1], s)
            L.append(L_i)

        return array(L).flatten()

    def compute_metrics(self, X: Matrix, force: bool = False) -> bool:
        """
        Calculate and log metrics for batch `X`.

        Returns:
            bool: Whether metrics were calculated.
        """
        if (
            self.log_every_n_iterations is not None
            and self.iteration_step % self.log_every_n_iterations == 0
        ) or force:

            for metric_function_name in self.metrics:
                metric_function = getattr(self, metric_function_name)

                # For training data.
                metric_value = metric_function(X)

                if isinstance(metric_value, np.ndarray):
                    metric_value = metric_value.mean()
                self.training_metrics_[metric_function_name].append(metric_value)

                # And for validation set.
                if self.X_validation is not None:
                    metric_value = metric_function(self.X_validation)
                    if isinstance(metric_value, np.ndarray):
                        metric_value = metric_value.mean()
                    self.validation_metrics_[metric_function_name].append(metric_value)
            return True

        return False

    def print_metrics(self):
        """
        Print out last metric value.
        """
        train_keys = sorted(self.training_metrics_.keys())
        valid_keys = sorted(self.validation_metrics_.keys())

        latest_training_metric = [self.training_metrics_[key][-1] for key in train_keys]
        latest_valid_metric = [self.validation_metrics_[key][-1] for key in valid_keys]

        latest_metrics_combined = latest_training_metric + latest_valid_metric

        # Don't print anything if no metrics are calculated.
        if len(latest_metrics_combined) == 0:
            return

        # Make a table combining train and validation fields.
        # 1) Determine column format based on metric type (float v.s. array).
        column_format = "{0:<5}"
        for i, value in enumerate(latest_metrics_combined):
            if isinstance(value, float):
                column_format += "{" + str(i + 1) + ":<22.4f}"
            elif isinstance(value, (tuple, list)):
                # Make columns for individual elements of array.
                column_format += "".join(
                    "{" + str(i + 1) + "[" + str(k) + "]}   " for k in range(len(value))
                )
            else:
                column_format += "{" + str(i + 1) + "}"

        # Print header.
        if self.iteration_step == 0:
            header_train = [f"{key}_train" for key in train_keys]
            header_valid = [f"{key}_val" for key in train_keys]
            header = ["Epoch"] + header_train + header_valid
            header_format = re.sub(r"\[\d+\]", "", column_format.replace(".4f", ""))
            print(header_format.format(*header))

        with np.printoptions(precision=4, floatmode="fixed"):
            print(
                column_format.format(
                    self.mini_batcher_iterator_.current_epoch,
                    *latest_metrics_combined,
                )
            )

    def _stop_iteration(self, *parameter_updates) -> bool:
        """
        Are the parameters converged or is the maximum iteration number exceeded?
        """
        if self.maximum_iteration > 0 and self.iteration_step >= self.maximum_iteration:
            if self.verbose:
                print("Terminated, exceeded maximum number of iterations.")
            return True

        # Check convergence of parameters every 100 iterations, using the size
        # of all parameter updates.
        if self.iteration_step % 100 == 0:
            parameters_converged = map(
                lambda x: np.all(abs(x) < self.tolerance), parameter_updates
            )
            if np.fromiter(parameters_converged, dtype=bool).all():
                if self.verbose:
                    print("Iteration converged!")
                return True

        return False

    def _unpack(self, X: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Unpack variables from `X`.
        """
        return (
            get_columns(X, self.visible_columns_),
            get_columns(X, self.event_columns),
        )

    def _compress(self, xi: Matrix, event: Matrix) -> Matrix:
        """
        Inverse operation of `_unpack`.
        """
        m = xi.shape[0]
        n = xi.shape[1] + event.shape[1]

        if self.visible_columns and isinstance(self.visible_columns[0], str):
            X = pd.DataFrame()
        else:
            X = zeros(shape=[m, n])

        X = self._set_columns(X, xi, self.visible_columns_)
        X = self._set_columns(X, event, self.event_columns)

        return X

    def _inflate(self, X: Matrix) -> Tuple[Matrix, Matrix]:
        """
        No additional inflation (to triplets) is necessary.
        """
        return self._unpack(X)

    def p_h_condition_x(self, X: Matrix) -> Matrix:
        """
        Calculate latent activation probability conditioned on observations p(h=1|x).
        """
        return sigmoid(-self.phi(X))

    def sample_h(self, X: Matrix) -> Matrix:
        """
        Sample hidden units from conditional distribution h ~ p(h|x).

        Args:
            X (array[m x n_v]): Visible units to condition on.

        Returns:
            Matrix[m x n_h]: Binary unit activations (i.e., latent samples).
        """

        # Calculate p(h=1|x).
        P = self.p_h_condition_x(X)

        # Number of records.
        m = P.shape[0]
        U = np.random.uniform(size=(m, self.n_hidden_units))

        # Turn hidden unit on when probability is larger than random uniform number,
        H = (P > U).astype(float64)
        return H

    def transform(
        self, X: Matrix, y=None, reconstruction_steps: Optional[int] = None
    ) -> Matrix:
        """
        Impute the missing and censored events, and calculate the latent activations.
        """
        if not self.has_missing_data(X):
            xi, _ = self._unpack(X)
            return self.p_h_condition_x(xi)

        if reconstruction_steps is None:
            reconstruction_steps = self.CD_steps
        xi_reconstr = self.impute(X, reconstruction_steps=reconstruction_steps)
        return self.p_h_condition_x(xi_reconstr)

    def impute(self, X: Matrix, reconstruction_steps: int = 1) -> MatrixTriplet:
        """
        Impute the unclamped variables.
        """
        xi, event = self._inflate(X)

        xi_reconstr = self._copy(xi)
        for _ in range(reconstruction_steps):
            xi_reconstr = self.gibbs_wake_update(xi_reconstr, observation=(xi, event))
        return xi_reconstr

    def gibbs_update(self, X: np.ndarray) -> np.ndarray:
        """
        Perform a single Gibbs update step on X.
        """
        H = self.sample_h(X)
        X = self.sample_x(H)
        return X

    def partition_function(self) -> float:
        """
        Calculate the partition function Z.

        Z = sum_h exp[-F(h)] = sum_{x,h} exp[-E(x,h)].
        """
        H = generate_binary_permutations(n=self.n_hidden_units)
        F = self.free_energy_h(H)
        Z = np.exp(-F).sum()
        return Z

    def log_partition_function(self) -> float:
        """
        Calculate ln [Z] with Z the partition function.

        Z = sum_h exp[-F(h)] = sum_{x,h} exp[-E(x,h)].
        """
        H = generate_binary_permutations(n=self.n_hidden_units)
        F = self.free_energy_h(H)
        # Wrap in one expression to prevent exploding numbers.
        return np.log(np.exp(-F).sum())

    def log_likelihood(self, X: Matrix) -> np.ndarray:
        """
        Calculate the log-likelihood using the modified free energy function F(x).

        See `free_energy_x` for more details.
        """
        likelihood = -self.free_energy_x(X) - np.log(self.partition_function())
        return likelihood

    def average_log_likelihood(self, *args, **kwargs) -> float:
        """
        Log likelihood normalised to number of samples `m`.
        """
        return self.log_likelihood(*args, **kwargs).mean()

    def update_parameters(self, gradient_update: Dict[str, np.ndarray]):
        """
        Update the free parameters using a single gradient ascent parameter update.
        """
        for i, param_name in enumerate(self.parameters):
            parameter = getattr(self, param_name)
            update = self.momentum_fraction * self.previous_update[
                param_name
            ] - self.eps[i] * (
                # Minus sign because p ~ exp[-E(x,h)] and thus -<d/dx E(x,h)>.
                gradient_update[param_name]
                # L2 regularisation; overall minus sign because we are doing
                # gradient ascent and want to shrink W^2.
                + self.weight_decay_[i] * parameter
            )
            parameter += update
            self.previous_update[param_name] = update

    def single_contrast_div_iteration(self, X_batch: Matrix) -> bool:
        """
        Do a single k-step (persistent) contrastive divergence (CD) iteration.

        Args:
            X_batch (Matrix): Do a CD iteration using this mini batch.

        Returns:
            bool: Stop iteration?
        """
        xi_batch, event_batch = self._inflate(X_batch)
        # The starting point of the Gibbs sleep chain is either:
        # 1) a data point for constrastive divergence,
        # 2) the previous state for persistent contrastive divergence.
        X = self._copy(xi_batch)
        if self.persistent and self.X_previous_sleep is not None:
            X_prime = self.X_previous_sleep
        else:
            X_prime = self._copy(xi_batch)

        # Do `k` Gibbs steps.
        for _ in range(0, self.CD_steps):
            X = self.gibbs_wake_update(X, observation=(xi_batch, event_batch))
            X_prime = self.gibbs_sleep_update(X_prime)

        # Calculate average activation E[h|x] given reconstructed data x.
        MU = self.p_h_condition_x(X)
        MU_prime = self.p_h_condition_x(X_prime)

        # Update parameters using gradient ascent.
        try:
            with np.errstate(invalid="raise"):
                grad_wake = self.energy_gradient(X, MU)
                grad_sleep = self.energy_gradient(X_prime, MU_prime)
        except FloatingPointError:
            raise FloatingPointError(
                "Numerical overflow, try to reduce the learning rate."
            )
        grad_update = {k: grad_wake[k] - grad_sleep[k] for k in self.parameters}
        self.update_parameters(grad_update)

        if self.persistent:
            self.X_previous_sleep = X_prime

        param_updates_sorted = (grad_update[k] for k in self.parameters)
        return self._stop_iteration(*param_updates_sorted)

    def gibbs_wake_update(
        self, X: MatrixOrTriplet, observation: Observation
    ) -> MatrixOrTriplet:
        """
        Perform a single Gibbs update step on X using observation constraint.
        """
        xi, event = observation
        if isinstance(event, tuple) and sum(e.size for e in event) == 0:
            return xi
        elif isinstance(event, np.ndarray) and event.size == 0:
            return xi
        H = self.sample_h_wake(X)
        return self.sample_x_wake(H, observation)

    def gibbs_sleep_update(self, X: Matrix) -> Matrix:
        """
        Perform a single Gibbs update step on `X`.
        """
        H = self.sample_h_sleep(X)
        return self.sample_x_sleep(H)

    def sample_x_wake(self, H: Matrix, observation: Observation) -> MatrixOrTriplet:
        """
        Sample x ~ p[x|h, o=(xi, e)].
        """
        xi, event = observation
        if event.size == 0:
            return xi
        raise NotImplementedError("No support implemented for censoring.")

    def sample_x_sleep(self, H: Matrix) -> MatrixOrTriplet:
        """
        Sample from distribution x ~ p(x|h).
        """
        return self.sample_x(H)

    def sample_h_wake(self, X: MatrixOrTriplet):
        """
        Sample hidden activations h ~ p(h|x).
        """
        return self.sample_h(X)

    def sample_h_sleep(self, X: MatrixOrTriplet) -> Matrix:
        """
        Sample hidden activations from the right truncated gamma distribution.
        """
        return self.sample_h(X)

    def persistent_constrastive_divergence(self, X: Matrix):
        """
        Perform k-step (persistent) contrastive divergence.

        For more information see Refs. [1] and [2].
        """
        self.iteration_step = 0
        # Make iterator that generates mini batches.
        self.mini_batcher_iterator_ = MiniBatchIterator(
            X,
            mini_batch_size=self.mini_batch_size,
            number_of_epochs=self.n_epochs,
            shuffle_each_epoch=True,
        )

        for X_batch in iter(self.mini_batcher_iterator_):
            stop_iteration = self.single_contrast_div_iteration(X_batch)

            if stop_iteration:
                break

            # Compute metrics on the raw (i.e., non-unpacked) data.
            if self.compute_metrics(X) and self.verbose:
                self.print_metrics()

            self.iteration_step += 1

        # Always log the last iteration.
        self.compute_metrics(X, force=True)
        if self.verbose:
            self.print_metrics()

    def modified_free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate modified free energy F(x) in presence of censoring.

        We use a modified definition that directly links to the likelihood:
        exp[-F(xi)] = sum_h integral dx exp[-E(x,h)] g(x,o).
        so that
        likelihood(o) = integral dx p(x) g(x, o) = -F(x) - ln Z

        instead of
        exp[-F(x)] = sum_h exp[-E(x,h)].
        """
        xi, event = self._unpack(X)
        if event.size == 0:
            return self.free_energy_x(xi)
        raise NotImplementedError

    @abstractmethod
    def energy_gradient(self, X: Matrix, H: Matrix) -> Dict[str, np.ndarray]:
        """
        Calculate gradient of energy w.r.t. fitting parameters.

        E.g., <d/dW E(x, h)> = <x_i h_j> for the visible-hidden coupling matrix.
        """

    @abstractmethod
    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(x) of visible units.

        where F(x) is defined as
        exp[-F(x)] = sum_h exp[-E(x,h)].

        Args:
            X (array[m x n_v]): Visible units.

        Returns:
            array[m]: Free energy for each row.
        """

    @abstractmethod
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

    @abstractmethod
    def energy(self, X: Matrix, H: Matrix) -> np.ndarray:
        """
        Energy function of the model.

        Args:
            X (array[m x n_v]): Visible units.
            H (array[m x n_h]): Hidden units.

        Returns:
            array[m]: Energy for each row (X, H).
        """

    @abstractmethod
    def sample_x(self, H: Matrix) -> np.ndarray:
        """
        Sample visible units from the conditional distribution x ~ p(x|h).

        Args:
            H (array[m x n_h]): Activations to condition on.

        Returns:
            np.ndarray[m x n_v]: Samples of visible units.
        """

    @abstractmethod
    def phi(self, X: Matrix) -> Matrix:
        """
        Latent state bias, large positive (negative) `phi` (de)activates the state.

        Args:
            X (Matrix[m x n_v]): States of the visible units.
        Returns:
            Matrix[m x n_h]: Bias of the hidden units.
        """

    @abstractmethod
    def initialise_parameters(self, X: Optional[Matrix] = None):
        """
        Initialise training parameteres, possibly using training data `X`.

        This method should set `parameters_initialised_` to True.
        """

    def pseudo_likelihood(self, X: np.ndarray, i: int) -> np.ndarray:
        """
        Calculate the pseudo-likelihood P(x_i | x_{j!=i}) for a given `i`.
        """
        raise NotImplementedError("This function is not implemented by the model.")
