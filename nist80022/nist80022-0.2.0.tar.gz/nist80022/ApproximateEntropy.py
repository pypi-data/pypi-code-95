import math
from typing import List, Tuple

import numpy as np
from scipy.special import gammaincc

class ApproximateEntropy:

    @staticmethod
    def approximate_entropy_test(
            binary_data:str, verbose=False, pattern_length=10
    ) -> List[Tuple[str, float, bool]]:
        """
        from the NIST documentation http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        As with the Serial test of Section 2.11, the focus of this test is the frequency of all possible
        overlapping m-bit patterns across the entire sequence. The purpose of the test is to compare
        the frequency of overlapping blocks of two consecutive/adjacent lengths (m and m+1) against the
        expected result for a random sequence.

        :param      binary_data:        a binary string
        :param      verbose             True to display the debug message, False to turn off debug message
        :param      pattern_length:     the length of the pattern (m)
        :return:    [(test_name, p_value, bool)] A tuple containing the test_name, p_value and
            pass/fail result of the test.
        """
        length_of_binary_data = len(binary_data)

        # Augment the n-bit sequence to create n overlapping m-bit sequences by appending m-1 bits
        # from the beginning of the sequence to the end of the sequence.
        # NOTE: documentation says m-1 bits but that doesnt make sense, or work.
        binary_data += binary_data[:pattern_length + 1:]

        # Get max length one patterns for m, m-1, m-2
        max_pattern = ''
        for i in range(pattern_length + 2):
            max_pattern += '1'

        # Keep track of each pattern's frequency (how often it appears)
        vobs_01 = np.zeros(int(max_pattern[0:pattern_length:], 2) + 1)
        vobs_02 = np.zeros(int(max_pattern[0:pattern_length + 1:], 2) + 1)

        for i in range(length_of_binary_data):
            # Work out what pattern is observed
            vobs_01[int(binary_data[i:i + pattern_length:], 2)] += 1
            vobs_02[int(binary_data[i:i + pattern_length + 1:], 2)] += 1

        # Calculate the test statistics and p values
        vobs = [vobs_01, vobs_02]

        sums = np.zeros(2)
        for i in range(2):
            for j in range(len(vobs[i])):
                if vobs[i][j] > 0:
                    sums[i] += vobs[i][j] * math.log(vobs[i][j] / length_of_binary_data)
        sums /= length_of_binary_data
        ape = sums[0] - sums[1]

        xObs = 2.0 * length_of_binary_data * (math.log(2) - ape)

        p_value = gammaincc(pow(2, pattern_length - 1), xObs / 2.0)

        if verbose:
            print("Approximate Entropy Test:")
            print("  {:<40}{:>20}".format("Length of input:", length_of_binary_data))
            print("  {:<40}{:>20}".format("Length of each block:", pattern_length))
            print("  {:<40}{:>20}".format("ApEn(m):", ape))
            print("  {:<40}{:>20}".format("xObs:", xObs))
            print("  {:<40}{:>20}".format("P-Value:", p_value))

        return [("approximate_entropy_test", p_value, (p_value >= 0.01))]
