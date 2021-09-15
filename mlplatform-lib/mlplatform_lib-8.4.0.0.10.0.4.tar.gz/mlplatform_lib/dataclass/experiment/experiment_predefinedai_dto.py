from dataclasses import dataclass

@dataclass
class ExperimentPredefinedaiDto:
    id: int
    authorization_id: int
    experiment_type: str
    name: str
    namespace: str
    pvc_name: str
    pvc_size: str
    created_on: str
    description: str
    do_id: int
    task_type: str