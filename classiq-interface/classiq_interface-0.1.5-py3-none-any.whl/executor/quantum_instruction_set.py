import enum


class QuantumInstructionSet(str, enum.Enum):
    QASM = "qasm"
    IONQ = "ionq"
