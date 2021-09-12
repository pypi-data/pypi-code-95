
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


# TODO maybe use optuna for hyperparameters!!


import torch
import torch.nn.functional as F

from nystrompca.base import Transformation


class AutoEncoder(torch.nn.Module, Transformation):

    def __init__(self, epochs: int = 1, **kwargs):

        torch.nn.Module.__init__(self)

        Transformation.__init__(self, **kwargs)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    def forward(self, x: torch.Tensor) -> torch.Tensor:

        h1 = F.relu(self.fc1(x))

        return self.fc2(h1)


    def fit_transform(self, X): # TODO try putting the train function as a member function...

        # Try simple fully connected on flattened data atm
        self.X = torch.Tensor(X)

        self.fc1 = torch.nn.Linear(X.shape[1], self.n_components)
        self.fc2 = torch.nn.Linear(self.n_components, X.shape[1])

        self.train()




    def transform(self, X_test):

        # TODO convert to Tensor then feed into the forward method I think...

        return 0

