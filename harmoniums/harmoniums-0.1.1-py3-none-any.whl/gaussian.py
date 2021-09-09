from typing import Dict, Optional, Tuple

import numpy as np

from harmoniums import BaseHarmonium
from harmoniums.const import Matrix
from harmoniums.wrappers import warn_unused_parameters


class GaussianHarmonium(BaseHarmonium):
    """
    Restricted Boltzmann machine with continuous visible, and binary hidden, units.

    Refs.
    [1]: Melchior et al., Gaussian-binary restricted Boltzmann machines for
    modeling natural image statistics, PloS 12, 0171015 ('17).

    [2]: Glorot & Bengio, Understanding the difficulty of training deep feedforward
    neural networks ('10).
    """

    # Free parameters of the model that can be fit (see `energy`).
    parameters = ("W", "a", "b", "sigma")
    # By default, don't apply weight decay to bias and standard deviation
    # parameters (see Hinton RBM tutorial).
    no_penalty = ("a", "b", "sigma")

    @warn_unused_parameters
    def initialise_parameters(self, X: Optional[Matrix] = None, event=None):
        """
        Initialise training parameteres.
        """
        # Weight initialisations according to Ref. [2].
        scale = np.sqrt(6 / (self.n_hidden_units + self.n_visible_units))
        self.W = np.random.uniform(
            -scale, scale, size=(self.n_visible_units, self.n_hidden_units)
        )

        # Standard deviations.
        self.sigma = np.ones(shape=(self.n_visible_units, 1))

        # Initialise the bias to 0.
        self.a = np.zeros((self.n_visible_units, 1))

        # Initialise bias according to Eq. (37) of Ref. [1], but slightly adapted to our
        # definition of the energy function.
        tau = 0.1
        self.b = (
            (self.W ** 2).sum(axis=0) / 2
            - (self.a / self.sigma).T @ self.W
            - np.log(tau)
        ).T
        self.b = self.b.reshape(-1, 1)

        self.is_parameters_initialised_ = True

    def energy(self, X: Matrix, H: Matrix) -> np.ndarray:
        """
        Energy function of Gaussian restricted Boltzmann machine.

        Args:
            X (Matrix[m x n_v]): Visible states.
            H (Matrix[m x n_h]): Hidden states.

        Returns:
            array[m]: Configurational energy of (x,h) pair.
        """
        # Gaussian part: (x_i - a_i)^2 / (2* sigma_i^2).
        G = (((X - self.a.T) / self.sigma.T) ** 2 / 2).sum(axis=1)
        # Linear part: x_i W_ij h_j / sigma_i.
        L = (X / self.sigma.T @ self.W * H).sum(axis=1)
        # Bias part (of the hidden variables).
        B = (H @ self.b).flatten()

        # Energy is a combination of the Gaussian, the linear and the bias terms.
        E = G + L + B
        return E

    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate the free energy F.

        exp[-F(x)] = sum_h exp[-E(x,h)]
        Args:
            X (Matrix[m x n_v]): Visibile states.

        Returns:
            array[m]: Free energy for each record
        """
        # z_j = sum_i x_i W_ij/sigma_i + b_j.
        Z = X / self.sigma.T @ self.W + self.b.T
        # Gaussian part: (x_i - a_i)^2 / (2 sigma_i^2)
        G = ((X - self.a.T) / self.sigma.T) ** 2 / 2
        F = (
            G.sum(axis=1)
            # Use identity: ln[sigmoid(z)] = -ln[1 + exp[-z]].
            - np.logaddexp(0, -Z).sum(axis=1)
        )
        return F

    def free_energy_h(self, H: Matrix) -> np.ndarray:
        """
        Calculate free energy for hidden units.

        exp[-F(h)] = sum_x exp[-E(x,h)]
        """
        # s_i^2 = (W_ij * h_j)^2 / 2.
        s = (H @ self.W.T) ** 2 / 2
        F_h = (
            # sum_i h_i b_i.
            (H @ self.b).flatten()
            # sum_{ij} a_i W_ij h_j / sigma_i.
            + (H @ self.W.T @ (self.a / self.sigma)).flatten()
            # sum_i (sum_j W_ij h_j)^2 / 2.
            - s.sum(axis=1)
            # sum_i 1/2 ln[2 pi sigma_i^2].
            - (np.log(2.0 * np.pi * self.sigma ** 2) / 2).sum(axis=0)
        )
        return F_h

    def phi(self, X: Matrix) -> Matrix:
        """
        Latent state bias, large positive (negative) `phi` (de)activates the state.

        Observe that the energy can be written as E = 1/2 [(x-a)/sigma]^2 + <phi(x)|h>.

        Args:
            X (Matrix[m x n_v]): States of the visible units.
        Returns:
            Matrix[m x n_h]: Bias of the hidden units.
        """
        return self.b.T + X / self.sigma.T @ self.W

    def reconstruct_mu_sigma(
        self, X: Matrix, event=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstruct mean and standard deviation based on visible states `X`.
        """
        H = self.p_h_condition_x(X)
        mu = self.mean_x(H)
        return mu.mean(axis=0), self.sigma.flatten()

    def mean_x(self, H: Matrix) -> Matrix:
        """
        Average visible states <x>_p(x|h) given the latent states h.
        """
        return self.a.T - H @ self.W.T * self.sigma.T

    def sample_x(self, H: Matrix) -> Matrix:
        """
        Sample visible units conditioned on hidden units `H`.
        """
        mu = self.mean_x(H)
        # Draw from Gaussian distribution with mean `mu` and standard deviation
        # `self.sigma`.
        return mu + np.random.normal(size=mu.shape, scale=abs(self.sigma).T)

    def energy_gradient(self, X: np.ndarray, H: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate gradient of energy w.r.t. fitting parameters.

        That is: <d/dtheta E(x, h)>.
        """
        m: int = X.shape[0]
        gradient = {}
        gradient["W"] = X.T @ H / m
        gradient["a"] = -X.mean(axis=0, keepdims=True).T
        gradient["b"] = H.mean(axis=0, keepdims=True).T
        # Gradient of sigma is decomposed in a linear and quadratic part.
        gaussian = (X - self.a.T) ** 2 / self.sigma.T ** 3
        linear = X * (H @ self.W.T) / self.sigma.T ** 2
        gradient["sigma"] = -(gaussian + linear).mean(axis=0, keepdims=True).T
        return gradient
