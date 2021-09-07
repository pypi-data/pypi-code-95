from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class ModelModifiersFromConstructions(Function):
    """Assign honeybee Radiance modifiers based on energy construction properties."""

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    use_visible = Inputs.str(
        description='A switch to indicate whether the assigned radiance modifiers '
        'should follow the solar properties of the constructions or the visible '
        'properties.', default='solar',
        spec={'type': 'string', 'enum': ['solar', 'visible']}
    )

    exterior_offset = Inputs.float(
        description='A number for the distance at which the exterior Room faces should '
        'be offset in meters. This is used to account for the fact that the exterior '
        'material layer of the construction usually needs a different modifier '
        'from the interior. If set to 0, no offset will occur and all assigned '
        'modifiers will be interior.', default=0
    )

    @command
    def model_modifiers_from_constructions(self):
        return 'honeybee-energy edit modifiers-from-constructions model.hbjson ' \
        '--{{self.use_visible}} --exterior-offset {{self.exterior_offset}} ' \
        '--output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its Radiance modifiers assigned based on its '
        'energy constructions.', path='new_model.hbjson'
    )
