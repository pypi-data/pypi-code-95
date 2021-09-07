from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class SimulateModel(Function):
    """Simulate a Model JSON file in EnergyPlus."""

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    ddy = Inputs.file(
        description='Optional design day file to be used in the sizing calculation '
        'if no design days are specified in the sim_par.',
        path='weather.ddy', extensions=['ddy'], optional=True
    )

    sim_par = Inputs.file(
        description='SimulationParameter JSON that describes the settings for the '
        'simulation.', path='sim-par.json', extensions=['json'], optional=True
    )

    additional_string = Inputs.str(
        description='An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects as a '
        'single string following the IDF format. This input can be used to include '
        'EnergyPlus objects that are not currently supported by honeybee.', default=''
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate model model.hbjson weather.epw ' \
            '--sim-par-json sim-par.json --additional-string ' \
            '"{{self.additional_string}}" --folder output'

    result_folder = Outputs.folder(
        description='Folder containing all simulation result files.',
        path='output/run'
    )

    hbjson = Outputs.file(
        description='A clean version of the input model that is in a format, which can '
        'be easily consumed by OpenStudio and directly matched to EnergyPlus results.',
        path='output/in.hbjson'
    )

    osm = Outputs.file(
        description='The OpenStudio model used in the simulation.',
        path='output/run/in.osm'
    )

    idf = Outputs.file(
        description='The IDF model used in the simulation.',
        path='output/run/in.idf'
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/run/eplusout.sql'
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/run/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/run/eplustbl.htm'
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/run/eplusout.err'
    )


@dataclass
class SimulateOsm(Function):
    """Simulate an OSM file in EnergyPlus."""

    osm = Inputs.file(
        description='Path to a simulate-able OSM file.', path='model.osm',
        extensions=['osm']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate osm model.osm weather.epw --folder output'

    idf = Outputs.file(
        description='The IDF model used in the simulation.',
        path='output/run/in.idf'
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/run/eplusout.sql'
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/run/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/run/eplustbl.htm'
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/run/eplusout.err'
    )


@dataclass
class SimulateIdf(Function):
    """Simulate an IDF file in EnergyPlus."""

    idf = Inputs.file(
        description='Path to a simulate-able IDF file.', path='model.idf',
        extensions=['idf']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate idf model.idf weather.epw --folder output'

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/eplusout.sql'
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/eplustbl.htm'
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/eplusout.err'
    )
