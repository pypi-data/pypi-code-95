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


"""Provide a molecular entity's proton dissociation constant model."""


from sqlalchemy import Column, Float, ForeignKey, Integer

from .mixin import ModelMixin
from .orm_base import ORMBase


class ORMProtonDissociationConstant(ModelMixin, ORMBase):
    """Define a molecular entity's proton dissociation constant model."""

    __tablename__ = "proton_dissociation_constants"

    molecule_id: int = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    value: float = Column(Float, nullable=False)
