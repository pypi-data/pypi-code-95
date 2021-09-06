import click
from tabulate import tabulate
from iictl.commands.volume.main import volume
from iictl.crud.persistent_volume_claim import list_persistent_volume_claim

@volume.command()
def ls():
    volume_list = list_persistent_volume_claim('notebook')
    volume_list = [{
        'name': it.metadata.name,
        'size': it.spec.resources.requests['storage'],
        'protection': it.metadata.annotations['deep.est.ai/volume-protection'] if 'deep.est.ai/volume-protection' in it.metadata.annotations else "false",
    } for it in volume_list.items]
    
    print(tabulate(volume_list, headers='keys'))