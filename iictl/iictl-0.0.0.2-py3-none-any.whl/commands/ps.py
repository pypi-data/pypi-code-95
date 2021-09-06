from tabulate import tabulate
from iictl.commands import cli
from iictl.crud.integrated_instance import list_integrated_instance

@cli.command()
def ps():
    iis = list_integrated_instance(
        namespace='notebook',
    )
    
    table = [{
        'name': ii['metadata']['name'],
        'image': ii['spec']['image'],
        'status': 'Unknown' if 'deploymentStatus' not in ii['status'] else ii['status']['deploymentStatus'], # TODO
    } for ii in iis['items']]
        
    print(tabulate(table, headers='keys'))