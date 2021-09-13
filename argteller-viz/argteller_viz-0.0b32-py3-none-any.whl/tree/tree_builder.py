from collections import defaultdict

from .tree_node import TreeNode

def construct_tree(parsed_node_data):

    parent_nodes = {}

    node_dicts = defaultdict(dict)
    value_dicts = defaultdict(dict)

    root = TreeNode(-2, 'root', None, 'root')
    parent_nodes[-2] = root

    for node_data in parsed_node_data:

        node_name, primary_type, secondary_type, depth, default_value, set_from = node_data

        if primary_type=='topic':
            depth = -1
            current_topic = node_name  # Topic has to be on the top of the dsl

        # Todo: also have set_to
        node = TreeNode(depth, node_name, default_value, primary_type, secondary_type, set_from=set_from)
        parent_nodes[depth] = node

        if not primary_type=='topic':

            node_dicts[current_topic][node_name] = node
            value_dicts[current_topic][node_name] = default_value

        parent_nodes[depth-1].add_child(node)

    return root, node_dicts, value_dicts


def merge_with_preset_tree(root, preset_value_dict):

    _merge_with_preset_tree(root, preset_value_dict)

def _merge_with_preset_tree(node, preset_value_dict):
    
    if node.primary_type == 'topic':
        
        preset_value_dict = preset_value_dict[node.name]

    if node.primary_type in ['param', 'optional']:
        
        if node.name in preset_value_dict:
            
            node.preset_value = preset_value_dict[node.name]
    
    for child in node.children:
        
        _merge_with_preset_tree(child, preset_value_dict)


def display_tree(root):

    print('node_name: primary_type, secondary_type, default_value, preset_value, set_from')
        
    _display_tree(root)
    
def _display_tree(node):

    depth = node.depth
    node_type = node.primary_type
    node_name = node.name

    if node_type != 'root':

        if node_type == 'topic':
            print()

            depth += 1

        print('    '*depth, node_name, ':', node.primary_type, node.secondary_type, node.default_value, node.preset_value)

    for child in node.children:

        _display_tree(child)

        