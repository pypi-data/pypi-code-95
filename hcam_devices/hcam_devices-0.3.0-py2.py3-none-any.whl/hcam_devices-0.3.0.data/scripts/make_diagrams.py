from hcam_devices.machines import get_yaml_file
from sismic.io import export_to_plantuml, import_from_yaml
from plantuml import PlantUML

import sys

name = sys.argv[1]
filename = get_yaml_file(name)
print(filename)
machine = import_from_yaml(filepath=filename)
plantuml = export_to_plantuml(machine)

maker = PlantUML(url='http://www.plantuml.com/plantuml/img/')
png_data = maker.processes(plantuml)

with open(name.replace('yaml', 'png'), 'wb') as out:
    out.write(png_data)
