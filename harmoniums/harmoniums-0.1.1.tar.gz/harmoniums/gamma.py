import numpy as np
from numpy import abs, all, log, random
from typing import Dict, Optional, Tuple

from harmoniums import BaseHarmonium
from harmoniums.const import Matrix
from harmoniums.distributions import normalisation_gamma_distribution
from harmoniums.samplers import sample_right_truncated_gamma_distribution


class GammaHarmonium(BaseHarmonium):
    """
    Restricted Boltzmann machine to model survival data.
    """

    # Free parameters of the model that can be fit (see `energy`).
    parameters = ("W", "V", "a", "b", "c")
    # By default, don't apply weight decay to bias and standard deviation
    # parameters.
    no_penalty = ("a", "b", "c", "sigma")

    def __init__(self, *args, **kwargs):
        self.guess_weights = kwargs.pop("guess_weights", False)
        super().__init__(*args, **kwargs)

    def initialise_parameters(self, X: Optional[Matrix] = None):
        """
        Initialise training parameteres.
        """
        # Glorot-Bengio weight initialisations.
        self.scale_ = np.sqrt(6 / (self.n_hidden_units + self.n_visible_units))
        self.W = random.uniform(
            -self.scale_, self.scale_, size=(self.n_visible_units, self.n_hidden_units),
        )
        self.V = random.uniform(
            0, self.scale_, size=(self.n_visible_units, self.n_hidden_units)
        )

        self.a = np.zeros((self.n_visible_units, 1))
        self.b = np.zeros((self.n_hidden_units, 1))
        self.c = random.uniform(0, self.scale_, size=(self.n_visible_units, 1))

        if X is not None and self.guess_weights:
            # 1. Initial guess from non-truncated gamma distribution.
            # <x> = alpha/beta.
            mu = X.mean(axis=0, keepdims=True).T
            # <x^2> - <x>^2 = alpha/beta^2.
            sigma = X.std(axis=0, keepdims=True).T
            beta_0 = mu / sigma
            alpha_0 = mu ** 2 / sigma
            # Set visible biases.
            self.c = np.where(alpha_0 != 0.0, alpha_0, self.c)
            self.a = beta_0

        self.is_parameters_initialised_ = True

    def fit(self, X: Matrix, y=None):
        """
        Check that the time variables are normalised to the unit range.
        """
        # Initialise the column names/indices so we can unpack.
        self._parse_column_names(X)
        xi, _ = self._unpack(X)

        assert all(xi >= 0) and all(xi <= 1)
        return super().fit(X, y)

    def energy(self, X: Matrix, H: Matrix) -> Matrix:
        """
        Energy function of the Gamma harmonium.

        E(x,h) = x_i W_{ij} h_j - ln[x_i] |V_{ij}| h_j
                + a_i x_i + b_j h_j + |c_i| ln[x_i].
        """
        ALPHA, BETA = self.alpha_beta(H)
        E = (X * BETA - log(X) * (ALPHA - 1)).sum(axis=1) + (H @ self.b).flatten()
        return E

    def phi(self, X: Matrix) -> Matrix:
        """
        Latent state bias, large positive (negative) `phi` (de)activates the state.

        Observe that the energy can be written as E = <x|a> + <phi(x)|h>.

        Args:
            X (Matrix[m x n_v]): States of the visible units.
        Returns:
            Matrix[m x n_h]: Bias of the hidden units.

        """
        return self.b.T + X @ self.W - log(X) @ abs(self.V)

    def alpha_beta(self, H: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Calculate shape (alpha) and rate (beta) parameters of the Gamma distribution.

        alpha(i) - 1 = sum_j|V(i,j)|h_j + |c_i| ln[x_i],
        beta(i) = sum_j W(i,j)h_j + a_i.
        """
        # Calculate alpha and beta from activations.
        ALPHA = H @ abs(self.V.T) + abs(self.c.T) + 1
        BETA = H @ self.W.T + self.a.T
        return (ALPHA, BETA)

    def reconstruct_alpha_beta(self, X: Matrix) -> Tuple[float, float]:
        """
        Reconstruct the truncated gamma distribution fit parameters (alpha and beta).
        """
        H = self.transform(X)
        alpha, beta = self.alpha_beta(H)
        return alpha.mean(axis=0), beta.mean(axis=0)

    def sample_x(self, H: Matrix) -> Matrix:
        """
        Sample from the modified gamma distribution.
        """
        ALPHA, BETA = self.alpha_beta(H)
        return sample_right_truncated_gamma_distribution(ALPHA, BETA, 1.0)

    def mean_x(self, H: Matrix) -> Matrix:
        """
        Average visible states <x>_p(x|h) given the latent states h.
        """
        ALPHA, BETA = self.alpha_beta(H)

        # Integral dx x p(x|h) = [b^a / gamma(a,b)] integral_0^1 dx x^(a) exp(-bx) =
        # 1/b gamma(a+1, b) / gamma(a,b)
        return normalisation_gamma_distribution(
            ALPHA + 1, BETA
        ) / normalisation_gamma_distribution(ALPHA, BETA)

    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(x) of visible units.

        exp[-F(x)] = sum_h exp[-E(x,h)]

        Args:
            X (Matrix[m x n_v]): Visible states.

        Returns:
            array[m]: Free energy corresponding to configurations `X`.
        """
        X, _ = self._unpack(X)

        # F(x) = -<ln x|c> + <x|a> - sum_i ln (1 + exp[-phi_i])
        # with phi_j = x_i W_ij + b_i + ln[x_i] |V_{ij}| (summation implied).
        PHI = self.phi(X)
        F = (
            (X @ self.a).flatten()
            - (log(X) @ abs(self.c)).flatten()
            - np.logaddexp(0, -PHI).sum(axis=1)
        )
        return F

    def free_energy_h(self, H: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(h) of hidden units.

        exp[-F(h)] = integral dx exp[-E(x,h)]
        """
        ALPHA, BETA = self.alpha_beta(H)
        free_energy = (H @ self.b).flatten() - log(
            normalisation_gamma_distribution(ALPHA, BETA)
        ).sum(axis=1)
        return free_energy

    def energy_gradient(self, X: np.ndarray, H: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate gradient of energy w.r.t. fitting parameters.

        That is: <d/dtheta E(x, h)>.
        """
        m: int = X.shape[0]
        gradient = {}
        gradient["V"] = -log(X).T @ H * np.sign(self.V) / m
        gradient["W"] = X.T @ H / m
        gradient["a"] = X.mean(axis=0, keepdims=True).T
        gradient["b"] = H.mean(axis=0, keepdims=True).T
        gradient["c"] = -np.sign(self.c) * log(X).mean(axis=0, keepdims=True).T
        return gradient
