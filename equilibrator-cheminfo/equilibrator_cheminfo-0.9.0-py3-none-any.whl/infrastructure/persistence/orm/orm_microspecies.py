# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""Provide a molecular entity's microspecies model."""


import pickle
from typing import Dict

from sqlalchemy import Boolean, Column, ForeignKey, Integer, PickleType, String

from equilibrator_cheminfo.helpers import shorten_string

from . import ORMBase
from .mixin import ModelMixin


class ORMMicrospecies(ModelMixin, ORMBase):
    """Define a molecular entity's microspecies model."""

    __tablename__ = "microspecies"

    molecule_id: int = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    is_major: bool = Column(Boolean, default=False, nullable=False)
    smiles: str = Column(String, nullable=False)
    charge: int = Column(Integer, nullable=False)
    atom_bag: Dict[str, int] = Column(
        PickleType(protocol=pickle.HIGHEST_PROTOCOL), nullable=False
    )

    def __repr__(self) -> str:
        """Return a representation string for this object."""
        return (
            f"{type(self).__name__}(molecule_id={self.molecule_id}, "
            f"is_major={self.is_major}, "
            f"SMILES={shorten_string(self.smiles)})"
        )
