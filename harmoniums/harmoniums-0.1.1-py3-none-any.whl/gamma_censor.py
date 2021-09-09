from typing import Optional, Tuple, Union

import numpy as np
from numpy import exp, zeros_like

from harmoniums import GammaHarmonium
from harmoniums.const import Matrix
from harmoniums.const import ObservationMatrix as Observation
from harmoniums.distributions import (
    normalisation_gamma_distribution,
    normalisation_gamma_interval_distribution,
)
from harmoniums.samplers import sample_interval_truncated_gamma_distribution
from harmoniums.utils import generate_binary_permutations, reset_random_state


class CensorGammaHarmonium(GammaHarmonium):
    """
    Restricted Boltzmann machine to model censored data.
    """

    def __init__(
        self,
        n_hidden_units: int = 5,
        n_visible_units: int = -1,
        # Scale of weights is ~ 1e-2, the learning rate is a factor 1e-3 smaller than
        # that [1].
        learning_rate: Union[float, Tuple[float, ...], list, dict] = 1e-1,
        random_state: int = 1234,
        CD_steps: int = 1,
        # Use this much from the previous update.
        momentum_fraction: float = 0.0,
        weight_decay: float = 0.0,
        mini_batch_size: int = 50,
        n_epochs: int = 10,
        log_every_n_iterations: Optional[int] = 25,
        maximum_iteration: int = 10000,
        tolerance: float = 1.0e-12,
        persistent: bool = False,
        verbose: bool = False,
        # Metrics to calculate during training.
        metrics: Tuple[str, ...] = ("reconstruction_error", "free_energy_x"),
        # Validation data for which to calculate the metrics.
        X_validation: Optional[np.ndarray] = None,
        # Initialise parameters by calling `fit`, but don't run constrative divergence.
        dry_run: bool = False,
        guess_weights: bool = False,
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
        self.random_state = random_state

        # Initialise empty list for all metrics to evaluate.
        self.metrics = metrics

        self.X_validation = X_validation
        self.guess_weights = guess_weights
        self.visible_columns = visible_columns
        self.event_columns = event_columns

        # Set random state.
        reset_random_state(random_state)

        self.is_parameters_initialised_ = False
        # Previous state (empty), when using persistent contrastive divergence.
        self.X_previous_sleep = None

    def sample_x_wake(self, H: Matrix, observation: Observation) -> Matrix:
        """
        Sample x ~ p[x|h, o=(xi, e)].
        """
        xi, event = observation
        if event.size == 0:
            return xi

        # Number of records.
        X = zeros_like(xi)
        mask = event.astype(bool)

        # Clamp observations.
        X[mask] = xi[mask]
        # Sample censored variables.
        if X[~mask].size > 0:
            ALPHA, BETA = self.alpha_beta(H)
            X[~mask] = sample_interval_truncated_gamma_distribution(
                ALPHA[~mask], BETA[~mask], xi[~mask]
            )
        return X

    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate modified free energy F(x) in presence of censoring.
        """
        xi, event = self._unpack(X)
        if event.size != 0:
            return self.modified_free_energy_x(X)
        return super().free_energy_x(X)

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
        mask = event.astype(bool)
        m = xi.shape[0]

        Z = np.zeros(m)
        # We can no longer carry out the summation
        # sum_h exp[-E(x,h)]
        # analytically, so we have to resort to numerical computation over all states.
        for h in generate_binary_permutations(self.n_hidden_units):
            # Do the sum over `h` for all `m` records in X. => Repeat `h` m times.
            H = h.reshape(1, -1).repeat(m, axis=0)
            alpha, beta = self.alpha_beta(H)

            # Calculate product of unnormalised probabilities.
            p = np.zeros((m, self.n_visible_units))
            # 1) Probability density (unnormalised) when event is observed.
            p[mask] = xi[mask] ** (alpha[mask] - 1) * exp(-beta[mask] * xi[mask])
            # 2) Interval distribution (unnormalised) when censored.
            if p[~mask].size > 0:
                p[~mask] = normalisation_gamma_interval_distribution(
                    alpha[~mask], beta[~mask], t_left=xi[~mask], t_right=1.0
                )
            Z += np.prod(p, axis=1) * exp(-H @ self.b).flatten()
        return -np.log(Z)

    def reconstruct_alpha_beta(self, X: Matrix) -> Tuple[float, float]:
        """
        Calculate alpha and beta for model based on `samples`.
        """
        H = self.transform(X)
        alpha, beta = self.alpha_beta(H)
        return alpha.mean(axis=0), beta.mean(axis=0)

    def mean_x(self, X: Matrix, H: Matrix) -> Matrix:
        """
        Average visible states <x>_p(x|h, o) for the conditional distribution.
        """
        XI, event = self._unpack(X)
        mask = event.astype(bool)
        ALPHA, BETA = self.alpha_beta(H)
        mean = zeros_like(XI)

        # Integral dx x p(x|h) = [b^a / gamma(a,b)] integral_0^1 dx x^(a) exp(-bx) =
        # 1/b gamma(a+1, b) / gamma(a,b)
        if mean[mask].size > 0:
            mean[mask] = normalisation_gamma_distribution(
                ALPHA[mask] + 1, BETA[mask]
            ) / normalisation_gamma_distribution(ALPHA[mask], BETA[mask])

        if mean[~mask].size > 0:
            # The mean of an unobserved event should be larger.
            mean[~mask] = normalisation_gamma_interval_distribution(
                ALPHA[~mask] + 1, BETA[~mask], XI[~mask]
            ) / normalisation_gamma_interval_distribution(
                ALPHA[~mask], BETA[~mask], XI[~mask]
            )

        return self._compress(mean, event)
