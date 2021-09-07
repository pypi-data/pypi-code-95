import unittest
import numpy as np
import supernest as sn


class TestSupernestExceptions(unittest.TestCase):
    def test_bounds_transposed_is_caught(self):
        mu = np.array([1, 2, 3])
        sigma = np.array([[1, 2, 3], [3, 6, 8], [4, 5, 3]])
        bounds = np.array([[1, 2, 3], [4, 5, 6]]).T
        self.assertTrue(len(mu == len(sigma)))
        self.assertTrue(len(mu == len(sigma[0])))
        self.assertWarnsRegex(UserWarning, 'Bounds should be transposed.',
                              sn.gaussian_proposal, *[bounds, mu, sigma])

    def test_lopsided_bounds(self):
        mu = np.array([1, 2, 3])
        sigma = np.array([[1, 2, 3], [3, 6, 8], [4, 5, 3]])
        bounds = np.array([[1, 2, 3], [4, 5, 6, 7]], dtype=object)
        self.assertTrue(len(bounds[0]) != len(bounds[1]))
        self.assertRaisesRegex(ValueError, 'Lopsided bounds',
                               sn.gaussian_proposal, *[bounds, mu, sigma])

    def test_incompatible_bounds(self):
        mu = np.array([1, 2, 3])
        sigma = np.array([[1, 2, 3], [3, 6, 8], [4, 5, 3]])
        bounds = np.array([[1, 2, 3, 4], [4, 5, 6, 7]], dtype=object)
        self.assertTrue(len(bounds[0]) == len(bounds[1]))
        self.assertTrue(len(bounds[0]) != len(mu))
        self.assertRaisesRegex(
            ValueError,
            'Proposal mean and boundaries are of imcompatible length',
            sn.gaussian_proposal, *[bounds, mu, sigma])

    def test_mu_doesnt_match_cov(self):
        mu = np.array([1, 2, 3, 4])
        sigma = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        bounds = (np.array([0, 1, 2, 3]), np.array([-0, -1, -2, -3]))
        self.assertTrue(len(mu) != len(sigma))
        self.assertRaises(ValueError, sn.gaussian_proposal,
                          *[bounds, mu, sigma])
        sigma2 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        self.assertTrue(len(mu) == len(sigma2))
        self.assertTrue(len(mu) != len(sigma2[0]))
        self.assertRaisesRegex(ValueError, 'Dimensions of covariance and mean',
                               sn.gaussian_proposal, *[bounds, mu, sigma2])


if __name__ == "__main__":
    unittest.main()
