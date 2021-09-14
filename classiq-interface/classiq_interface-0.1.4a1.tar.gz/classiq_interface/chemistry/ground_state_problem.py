from enum import Enum

import pydantic
from classiq_interface.chemistry import molecule, hamiltonian_reduction


class FermionMapping(str, Enum):
    jordan_wigner = "jordan_wigner"
    parity = "parity"
    bravyi_kitaev = "bravyi_kitaev"
    fast_bravyi_kitaev = "fast_bravyi_kitaev"


class GroundStateProblem(pydantic.BaseModel):
    molecule: molecule.Molecule
    basis: str = pydantic.Field(default="sto3g", description="basis set")
    mapping: FermionMapping = pydantic.Field(
        default="jordan_wigner", description="fermionc mapping type"
    )
    reductions: hamiltonian_reduction.HamiltonianReduction
