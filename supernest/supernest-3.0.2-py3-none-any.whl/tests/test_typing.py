import unittest
import supernest as sn
import numpy as np


class TestTyping(unittest.TestCase):
    def test_proposal_is_proper_return_type(self):
        bounds = (0, 1)
        mean = np.array([0])
        stdev = np.array([[1]])
        proposal = sn.gaussian_proposal(bounds, mean, stdev)
        self.assertIsInstance(proposal, sn.Proposal)
        self.assertIsInstance(sn.superimpose([proposal, proposal]),
                              sn.Proposal)
        self.assertIsInstance(sn.superimpose([proposal, proposal], nDims=1),
                              sn.NDProposal)


if __name__ == '__main__':
    unittest.main()
