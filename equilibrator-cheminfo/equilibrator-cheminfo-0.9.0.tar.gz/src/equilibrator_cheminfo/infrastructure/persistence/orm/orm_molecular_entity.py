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


"""Provide a molecular entity model with dissociation constants and microspecies."""


import re
from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, validates

from .mixin import ModelMixin
from .orm_base import ORMBase
from .orm_error_message import ORMErrorMessage
from .orm_microspecies import ORMMicrospecies
from .orm_proton_dissociation_constant import ORMProtonDissociationConstant


class ORMMolecularEntity(ModelMixin, ORMBase):
    """
    Define a molecular entity in the context of microspecies.

    A molecular entity is defined in [1]_. The molecular entity is the root ORM model
    that contains cheminformatics predictions about dissociation
    constants and microspecies. Since pH ranges are considered, the entered InChIKey
    and InChI are expected to be in neutral protonation state.

    Attributes
    ----------
    id : int
        The primary key in the table.
    inchikey : str
        InChIKey is a hash of the full InChI with a constant length.
    inchi : str
        InChI descriptor of the molecule.
    dissociation_constants : list
        A list of float, which are the pKa values of this molecule.
    microspecies : list
        The compound's microspecies in a one-to-many relationship
    errors : list
        A collection of error messages associated with a molecule when using different
        cheminformatics software.

    References
    ----------
    .. [1] https://goldbook.iupac.org/terms/view/M03986

    """

    __tablename__ = "molecules"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    inchikey: str = Column(String(27), nullable=False, index=True, unique=True)
    # The InChI should be indexed and unique but can be too long for standard index.
    inchi: str = Column(String, nullable=False)
    proton_dissociation_constants: List[ORMProtonDissociationConstant] = relationship(
        "ORMProtonDissociationConstant",
        cascade="all, delete-orphan",
        lazy="select",
    )
    pka_values: List[float] = association_proxy(
        "proton_dissociation_constants",
        "value",
        creator=lambda value: ORMProtonDissociationConstant(value=value),
    )
    microspecies: List[ORMMicrospecies] = relationship(
        "ORMMicrospecies", cascade="all, delete-orphan", lazy="select"
    )
    error_messages: List[ORMErrorMessage] = relationship(
        "ORMErrorMessage",
        cascade="all, delete-orphan",
        lazy="select",
    )

    _inchikey_pattern = re.compile(r"[A-Z]{14}-[A-Z]{10}-N")
    _proton_layer_pattern = re.compile(r"/p.*?(/|$)")

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return f"{type(self).__name__}(id={self.id}, inchikey={self.inchikey})"

    @validates("inchikey")
    def validate_inchikey(self, _, inchikey: str) -> str:
        """Validate the format of the InChIKey and that it is not protonated."""
        assert self._inchikey_pattern.match(inchikey) is not None
        return inchikey

    @validates("inchi")
    def validate_inchi(self, _, inchi: str) -> str:
        """Assert that the given InChI does not contain a proton layer."""
        assert self._proton_layer_pattern.search(inchi) is None
        return inchi
