from typing import Dict, Optional

import numpy as np
from numpy import zeros
from scipy.special import expit as sigmoid

from harmoniums import BaseHarmonium
from harmoniums.const import Matrix
from harmoniums.wrappers import warn_unused_parameters


class BinaryHarmonium(BaseHarmonium):
    """
    Harmonium with binary visible units and binary hidden variables.

    Refs:
    [1]: G. E. Hinton, "A practical guide to training restricted Boltzmann machines." In
    Neural networks: Tricks of the trade, pp. 599-619. Springer, Berlin, Heidelberg,
    2012.
    """

    # Free parameters of the model that can be fit (see `energy`).
    parameters = ("W", "a", "b")
    # By default, don't apply weight decay to bias parameters (see Hinton RBM
    # tutorial).
    no_penalty = ("a", "b")

    @warn_unused_parameters
    def initialise_parameters(
        self, X: Optional[Matrix] = None, event: Optional[Matrix] = None,
    ):
        """
        Initialise training parameteres, possibly using training data `X`.
        """
        # Weight initialisations of `W` according to Ref. [1].
        self.W = np.random.normal(
            0.0, 0.01, size=(self.n_visible_units, self.n_hidden_units)
        )
        self.b = zeros(shape=(self.n_hidden_units, 1))
        if X is not None:
            # Initialise the bias using probabilities.
            p = X.mean(axis=0, keepdims=True).T
            # Set visible units according to ln[p/(1-p)], see Ref. [1].
            self.a = np.log(p / (1 - p), out=np.zeros_like(p), where=(p != 0))
        else:
            self.a = np.zeros(shape=(self.n_visible_units, 1))

        self.is_parameters_initialised_ = True

    def phi(self, X: Matrix) -> Matrix:
        """
        Latent state bias, large positive (negative) `phi` (de)activates the state.

        Observe that the energy can be written as E = <x|a> + <phi(x)|h>.
        """
        return self.b.T + X @ self.W

    def z(self, H: Matrix) -> Matrix:
        """
        Visible state bias, large positive (negative) `z` (de)activates the state.

        Args:
            H [m x n_h]: Latent biases.
        Returns:
            [m x n_v]: Bias values.
        """
        return self.a.T + H @ self.W.T

    def p_x_condition_h(self, H: np.ndarray) -> np.ndarray:
        """
        Calculate visible units conditioned on hidden variables p(x=1|h).
        """
        return sigmoid(-self.z(H))

    def sample_x(self, H: Matrix) -> Matrix:
        """
        Sample visible units conditioned on hidden units `H`.
        """
        # Number of records.
        m = H.shape[0]
        U = np.random.uniform(size=(m, self.n_visible_units))

        # Calculate p(x=1|h).
        P = self.p_x_condition_h(H)

        # Turn hidden unit on when probability is larger than random uniform number,
        X = (P > U).astype(int)
        return X

    def mean_x(self, H: Matrix) -> Matrix:
        """
        Average visible states <x>_p(x|h) given the latent states h.
        """
        return self.p_x_condition_h(H)

    def energy(self, X: Matrix, H: Matrix) -> Matrix:
        """
        Energy function of the Restricted Boltzmann machine.

        Note that we adopt the antiferromagnetic sign convention (i.e., the extra minus
        as in, e.g., Ref. [1] is absorbed in the fitting parameters).

        Args:
            X (Matrix[m x n_v]): Visible binary states.
            H (Matrix[m x n_h]): Hidden binary states.
        Returns:
            Matrix[m]: Returns energy of each record in `X` and `H`.
        """
        # Shape X: m x n_v.
        assert X.shape[1] == self.n_visible_units
        E = (X * self.z(H)).sum(axis=1, keepdims=True) + H @ self.b
        return E.flatten()

    def free_energy_x(self, X: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(x) of visible units.

        exp[-F(x)] = sum_h exp[-E(x,h)]
        """
        # F(x) = <x|a> - sum_i ln (1 + exp[-phi_i])
        # with phi_i = x_i W_ij + b_i.
        F = (X @ self.a).flatten() - np.logaddexp(0, -self.phi(X)).sum(axis=1)
        return F

    def free_energy_h(self, H: Matrix) -> np.ndarray:
        """
        Calculate the free energy F(h) of the hidden units.

        exp[-F(h)] = sum_x exp[-E(x,h)]
        """
        F = (H @ self.b).flatten() - np.logaddexp(0, -self.z(H)).sum(axis=1)
        return F

    def pseudo_likelihood(self, X: np.ndarray, i: int) -> np.ndarray:
        """
        Calculate the pseudo-likelihood P(x_i | x_{j!=i}) for a single i.

        P(x_i | x_{j!=i}) = exp(-F(x|i)) / [exp(-F(x|i)) + exp(-F(x|^i))] with x|^i the
        x_ith bit flipped.

        Equivalently, we can write
        P(x_i | x_{j!=i}) = sigmoid(dF_i(x)),
        with the free energy difference when flipping the bit.
        """
        # Convert float to binary by rounding.
        X_binary = np.round(X).astype(int)

        # Flip bit i.
        X_i_prime = X_binary.copy()
        X_i_prime[:, i] ^= 1

        # Free energy difference.
        dF = self.free_energy_x(X_i_prime) - self.free_energy_x(X_binary)
        return sigmoid(dF)

    def energy_gradient(self, X: np.ndarray, H: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate gradient of energy w.r.t. fitting parameters.

        That is: <d/dtheta E(x, h)>.
        """
        m: int = X.shape[0]
        gradient = {}
        gradient["W"] = X.T @ H / m
        gradient["a"] = X.mean(axis=0, keepdims=True).T
        gradient["b"] = H.mean(axis=0, keepdims=True).T
        return gradient
