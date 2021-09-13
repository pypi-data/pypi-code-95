import click
from tabulate import tabulate
from iictl.commands.main import cli
from iictl.crud.pod import list_pod
from iictl.crud.node import list_node
from collections import defaultdict

@cli.command(help='view resources')
def resources():
    pods = list_pod(
        field_selector='status.phase!=Failed,status.phase!=Succeeded',
    )
    
    node_resources = defaultdict(list)
    
    for pod in pods:
        spec = pod['spec']   

        if 'node_name' not in spec:
            continue
            
        for container in spec['containers']:
            if 'resources' not in container:
                continue
                
            node_resources[spec['node_name']].append(container['resources'])

    node_gpu_allocated = {}
    for node_name, resources in node_resources.items():
        gpu = 0
        
        for resource in resources:
            if resource['requests'] is None:
                continue
            
            gpu += int(resource['requests'].get('nvidia.com/gpu', '0'))
        
        node_gpu_allocated[node_name] = gpu
    
    
    nodes = list_node()
    
    node_gpu_capacity = {}
    for node in nodes:
        if 'nvidia.com/gpu' not in node['status']['capacity']:
            continue
            
        node_gpu_capacity[node['metadata']['name']] = int(node['status']['capacity']['nvidia.com/gpu'])
    
    node_gpu_allocatable = [{
        'node': node,
        'allocatable gpu': gpu - node_gpu_allocated[node],
    } for node, gpu in node_gpu_capacity.items()]
        
    
    click.echo(tabulate(node_gpu_allocatable, headers='keys'))
