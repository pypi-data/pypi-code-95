#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import click
import json
from sggo import app

@click.group()
@click.pass_context
def cli(ctx):
    """ Plumber SG: a command-line tool for the View Plumber SG. """
    click.echo('Please report any bug or issue to <wei.zou@corerain.com>')

@cli.command()
@click.argument('sg_json', type=click.Path(exists=True))
@click.option('--host', type=str, default='0.0.0.0')
@click.option('--port', type=int, default=5000)
def view(sg_json, host, port):
    ext = os.path.splitext(sg_json)[-1]
    if '.json' == ext:
        app.run(sg_json, host, port)
    else:
        data = parser(sg_json)
        app.run_with_json(data, host, port)


def parser(log_file):
    file_name = os.path.basename(log_file)
    sg_json = {
        'name': file_name.replace('.', '_'),
        'version': "4.0.0",
    }
    nodes = []
    edges = []
    in_map = {}
    node_op_map = {}
    index = 0
    with open(log_file, 'r') as f:
        for line in f.readlines():
            if 'op_index' not in line:
                continue
            target = line.replace(' ', '').split(';')
            name = target[0].split(':')[-1]
            fused_flag = target[1].split(':')[-1]
            op_type = target[2].split(':')[-1]
            inputs = target[3].split('input_layer_list:')[1]
            if len(inputs) > 0:
                inputs += ','
                inputs = inputs.split('),')[:-1]
                for n in inputs:
                    in_name = n.split('(')[0]
                    if in_name in node_op_map and node_op_map[in_name] == 'OP_CONST':
                        continue
                    shape = n.split('[')[1].split(']')[0]
                    if in_name not in in_map:
                        nodes.append({
                            'name': in_name,
                            'op': 'Input',
                            'input': [],
                            'output': [n]
                        })
                        in_map[in_name] = in_name
                    
                    edges.append({
                        'source': in_map[in_name], 
                        'target': name, 
                        'shape': shape.replace(',', 'x'), 
                        'label': (in_name + name).replace(':', '_').replace('.', '_')})

                inputs = [n + ')' for n in inputs]
            else:
                inputs = []
            
            outputs = target[4].split('output_layer_list:')[1]
            if len(outputs) > 0:
                outputs += ','
                outputs = outputs.split('),')[:-1]
                for n in outputs:
                    out_name = n.split('(')[0]
                    if out_name not in in_map:
                        in_map[out_name] = name
                    if out_name not in node_op_map:
                        node_op_map[out_name] = op_type

                outputs = [n + ')' for n in outputs]

            if op_type == 'OP_CONST':
                continue
            if op_type.startswith('OP'):
                op_type = op_type[3:]

            nodes.append({
                'name': name,
                'op': op_type,
                'input': inputs,
                'output': outputs,
                'fused_flag': fused_flag,
                '_layer_num': index
            })
            index += 1
        
        sg_json['node'] = nodes
        sg_json['edges'] = edges
    return sg_json


if __name__ == '__main__':
    cli()
