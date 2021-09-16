from collections import defaultdict

import pandas as pd

from .specification import SPECIFICATION


def parse_line(line, mdl_idx=0):
    """
    slice a string in specific spots (must include edges,
    left inclusive and right exclusive) and return appropriate types
    """
    line = line.strip()

    for record_type, spec in SPECIFICATION.items():
        if line.startswith(record_type):
            items = []
            for rng, dtype, colname in spec:
                if colname == 'model_id':
                    # special case for coordinates, add the model id
                    items.append(mdl_idx)
                else:
                    # split the line based on the specs
                    field = line[rng[0]:rng[1]]
                    if colname == 'bonds':
                        # special case for CONECT records, split the field in a list
                        field = [field[i * 5: (i + 1) * 5].strip() for i in range(9)]
                        items.append([int(f) for f in field if f != ''])
                        continue
                    try:
                        field = dtype(field.strip()) or None
                    except ValueError:
                        field = None
                    items.append(field)
            return record_type, items
    return None, None


def read_pdb(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    records = defaultdict(list)
    mdl_idx = 0
    # parse contents
    for line in lines:
        record_type, fields = parse_line(line, mdl_idx)
        if record_type == 'MODEL':
            mdl_idx = fields[0]
        elif record_type == 'ENDMDL':
            mdl_idx += 1
        elif record_type is not None:
            records[record_type].append(fields)

    # put in dataframes with appropriate column names
    data = {}
    for record_type, fields in records.items():
        _, _, columns = zip(*SPECIFICATION[record_type])
        df = pd.DataFrame(fields, columns=columns)
        data[record_type] = df

    return dict(data)
