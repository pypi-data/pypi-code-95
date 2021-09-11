from enum import Enum


class EntitySchemaType(str, Enum):
    CUSTOM_ENTITY = "custom_entity"
    DNA_SEQUENCE = "dna_sequence"
    AA_SEQUENCE = "aa_sequence"
    MIXTURE = "mixture"
    DNA_OLIGO = "dna_oligo"
    RNA_OLIGO = "rna_oligo"

    def __str__(self) -> str:
        return str(self.value)
