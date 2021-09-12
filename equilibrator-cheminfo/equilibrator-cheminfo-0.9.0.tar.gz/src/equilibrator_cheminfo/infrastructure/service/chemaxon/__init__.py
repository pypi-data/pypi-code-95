# Copyright (c) 2021, Moritz E. Beber.
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


"""Provide the ChemAxon adapter classes."""


from .chemaxon_error import ChemAxonError
from .chemaxon_molecule import ChemAxonMolecule
from .chemaxon_proton_dissociation_constants_service import (
    ChemAxonProtonDissociationConstantsService,
)
from .chemaxon_major_microspecies_service import ChemAxonMajorMicrospeciesService
from .chemaxon_molecular_entity_factory import (
    ChemAxonMolecularEntityFactory,
)
