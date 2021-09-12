
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


"""
Base parser object for arguments used by all experiments


Usage
~~~~~

::

    import argparse

    from nystrompca.experiments import base_parser

    parser = argparse.ArgumentParser(parents=[base_parser])

"""

import argparse

base_parser = argparse.ArgumentParser(add_help=False)

base_parser.add_argument('-n', default=1000, type=int,
                         help="total size of dataset")

base_parser.add_argument('-m', default=20, type=int,
                         help="size of subsampled dataset")

base_parser.add_argument('-d', default=10, type=int,
                         help="PCA dimension")

base_parser.add_argument('--kernel', default='rbf',
                         choices=['rbf', 'poly', 'linear', 'cosine',
                                  'laplace', 'cauchy'],
                         help="kernel function")

base_parser.add_argument('--save', action='store_true',
                         help="whether to save the plots on disk")

