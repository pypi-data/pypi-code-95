from typing import List, Optional, Tuple

import pydantic


class Molecule(pydantic.BaseModel):
    atoms: List[Tuple[str, Tuple[float, float, float]]] = pydantic.Field(
        description="List of atoms, each atom is a tuple of (name, location), name is a "
        "string and location is tuple of 3 floats representing its x,y,z coordinates"
    )
    spin: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=1, description="spin of the molecule"
    )
    charge: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=0, description="charge of the molecule"
    )
