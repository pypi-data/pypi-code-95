from typing import Optional

import pydantic
from qiskit import circuit as qiskit_circuit
from qiskit import qasm as qiskit_qasm


class CustomImplementation(pydantic.BaseModel):

    name: Optional[str] = pydantic.Field(
        default=None,
        description="The name of a custom function implementation",
    )

    _num_qubits_in_qasm: Optional[pydantic.conint(ge=1)] = pydantic.Field(default=None)

    single_implementation_quantum_circuit_qasm_string: pydantic.constr(
        min_length=1
    ) = pydantic.Field(description="The QASM code of a custom function implementation")

    @pydantic.validator("single_implementation_quantum_circuit_qasm_string")
    def validate_single_implementation_quantum_circuit_qasm_string(
        cls, single_implementation_quantum_circuit_qasm_string, values
    ):
        try:
            qc = qiskit_circuit.QuantumCircuit.from_qasm_str(
                single_implementation_quantum_circuit_qasm_string
            )
        except qiskit_qasm.exceptions.QasmError:  # The qiskit error is often extremely uninformative
            raise ValueError("The QASM string is not a valid quantum circuit.")
        values["_num_qubits_in_qasm"] = qc.num_qubits
        return single_implementation_quantum_circuit_qasm_string
