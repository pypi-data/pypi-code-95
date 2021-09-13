from .tree_node import TreeNode

import re
from collections import defaultdict


def check_type(line):
    if '/' in line:
        return 'param_setter'
    elif line[0:2]=='==':
        return 'string_sample'
    elif ('(' in line) & (')' in line):
        return 'alien'
    elif line[0]=='-':
        return 'param'
    elif line[0]=='=':
        return 'option'
    elif line[0]=='+':
        return 'optional'
    elif line[0]=='?':
        return 'boolean'
    elif line[0]=='#':
        return 'custom{}'.format(line[1])
    else:
        return 'topic'

def check_default(line):
    
    if not ':' in line:
        return line, None
    
    try:
        line_parts = line.split(':')
        line1, line2 = line_parts[0], ':'.join(line_parts[1:])

    except:

        print(line)
    
    if line2=='':
        return line1, None
    
    # if ',' in line2:
    
    #     line2, line3 = line2.split(',')

    #     if line3=='int':
    #         default_value = int(eval(line2))
    #     elif line3=='float':
    #         default_value = float(eval(line2))
    #     else:
    #         default_value = line2
            
    else:
        
        try:
            
            default_value = float(line2)
            
            if default_value.is_integer():
                default_value = int(default_value)
                
        except ValueError:
            
            default_value = line2

    line1 = line1.replace(" ", "")
            
    return line1, default_value

def get_depth(line):
    
    tab_depth = line.count('\t')
    space_depth = int((len(line) - len(line.lstrip(' ')))/4)
    return tab_depth + space_depth

def parse_dsl(dsl):

    parsed_node_data = []

    dsl_lines = dsl.splitlines()
    dsl_lines = dsl_lines + ['']

    depths = [0]

    for idx in range(1, len(dsl_lines)):

        primary_type = None

        prev_line = dsl_lines[idx-1]

        prev_depth = get_depth(prev_line)

        prev_line = prev_line.strip()

        if prev_line=='':
            pass
        else:
            # check the name portion of the prev_line
            # unless the : is there to support default value, : cannot occur in name itself

            prev_line_name = prev_line.split(':')[0]


            primary_type = check_type(prev_line_name)

        secondary_type = None

        line = dsl_lines[idx]

        depth = get_depth(line)

        line = line.strip()

        if line=='':
            pass
        elif prev_depth < depth:
            # if we don't have this condition, the deeper choice might
            # think it has shallower param induced from it
            secondary_type = check_type(line)

        set_from = None
        if primary_type=='alien':

            name, set_from = prev_line.split('(')

            name = re.sub('^[\s=+-?]+', '', name)
            set_from = set_from[0:-1]

        elif primary_type!='string_sample':

            try:

                name = re.sub('^[\s=+-]+', '', prev_line)
                int(name)
                name = str(name)

            except ValueError:

                name = re.sub('^[\s=+-?]+', '', prev_line)

            name, default_value = check_default(name)

        else:
            name = re.sub('^[\s=]+', '', prev_line)

            default_value = None
        
        if (primary_type=='param' or primary_type=='optional' or primary_type=='alien') and secondary_type is None:
            secondary_type = 'string'

        if primary_type=='boolean':
            primary_type = 'param'
            secondary_type = 'boolean'

        if name != '':
            parsed_node_data.append([name, primary_type, secondary_type, prev_depth, default_value, set_from])
            
    return parsed_node_data

