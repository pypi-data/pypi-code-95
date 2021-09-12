
# Copyright 2020 Fredrik Hallgren
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import numpy as np


class NystromMethod:

    """
    Base class for algorithms using the Nyström method

    Parameters
    ----------
    m_subset : int, default 10
        Size of Nyström subset

    """
    def __init__(self, m_subset: int = 10, **kwargs):

        self.m = m_subset

        self.subset = None


    def create_subset(self) -> None:
        """
        Randomly select a subset of *m* integers without replacement from
        all integers up to *n*. Sorts the selected subset in increasing order.

        Parameters
        ----------
        n : int
            Maximum sampled integer
        m : int
            Number of integers to sample

        Raises
        ------
        ValueError
            If *m* > *n*
        ValueError
            If the member *n* is not set

        """
        if self.n is None:
            raise ValueError("The total number of data points must be set.")

        subset = np.random.choice(range(self.n), self.m, replace=False)

        self.subset = np.sort(subset) # Not necessary but easier to debug

