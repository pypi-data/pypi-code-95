from typing import List, Tuple

import numpy as np
from scipy.stats import norm

class CumulativeSums:

    @staticmethod
    def cumulative_sums_test(
            binary_data:str, mode=0, verbose=False
    ) -> List[Tuple[str, float, bool]]:
        """
        from the NIST documentation http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        The focus of this test is the maximal excursion (from zero) of the random walk defined by the cumulative sum of
        adjusted (-1, +1) digits in the sequence. The purpose of the test is to determine whether the cumulative sum of
        the partial sequences occurring in the tested sequence is too large or too small relative to the expected
        behavior of that cumulative sum for random sequences. This cumulative sum may be considered as a random walk.
        For a random sequence, the excursions of the random walk should be near zero. For certain types of non-random
        sequences, the excursions of this random walk from zero will be large.

        :param      binary_data:    a binary string
        :param      mode            A switch for applying the test either forward through the input sequence (mode = 0)
                                    or backward through the sequence (mode = 1).
        :param      verbose         True to display the debug messgae, False to turn off debug message
        :return:    [(test_name, p_value, bool)] A tuple containing the test_name, p_value and
            pass/fail result of the test.
        """

        length_of_binary_data = len(binary_data)
        counts = np.zeros(length_of_binary_data)

        # Determine whether forward or backward data
        if not mode == 0:
            binary_data = binary_data[::-1]

        counter = 0
        for char in binary_data:
            sub = 1
            if char == '0':
                sub = -1
            if counter > 0:
                counts[counter] = counts[counter -1] + sub
            else:
                counts[counter] = sub

            counter += 1
        # Compute the test statistic z =max1≤k≤n|Sk|, where max1≤k≤n|Sk| is the largest of the
        # absolute values of the partial sums Sk.
        abs_max = np.max(np.abs(counts))

        start = int(np.floor(0.25 * np.floor(-length_of_binary_data / abs_max) + 1))
        end = int(np.floor(0.25 * np.floor(length_of_binary_data / abs_max) - 1))

        terms_one = []
        for k in range(start, end + 1):
            sub = norm.cdf((4 * k - 1) * abs_max / np.sqrt(length_of_binary_data))
            terms_one.append(norm.cdf((4 * k + 1) * abs_max / np.sqrt(length_of_binary_data)) - sub)

        start = int(np.floor(0.25 * np.floor(-length_of_binary_data / abs_max - 3)))
        end = int(np.floor(0.25 * np.floor(length_of_binary_data / abs_max) - 1))

        terms_two = []
        for k in range(start, end + 1):
            sub = norm.cdf((4 * k + 1) * abs_max / np.sqrt(length_of_binary_data))
            terms_two.append(norm.cdf((4 * k + 3) * abs_max / np.sqrt(length_of_binary_data)) - sub)

        p_value = 1.0 - np.sum(np.array(terms_one))
        p_value += np.sum(np.array(terms_two))

        if verbose:
            print("Cumulative Sums Test:")
            print("  {:<40}{:>20}".format("\tLength of input:\t", length_of_binary_data))
            print("  {:<40}{:>20}".format("\tMode:\t\t\t\t", mode))
            print("  {:<40}{:>20}".format("\tValue of z:\t\t\t", abs_max))
            print("  {:<40}{:>20}".format("\tP-Value:\t\t\t", p_value))
        test_type = ""
        if mode == 0:
            test_type = "forwards"
        elif mode == 1:
            test_type = "backwards"
        return [(f"cumulative_sums_test_{test_type}", p_value, (p_value >= 0.01))]
