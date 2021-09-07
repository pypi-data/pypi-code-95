import gzip

def read_fasta(path):
    name = None
    with (gzip.open if path.endswith('.gz') else open)(path, 'rt') as fasta:
        for line in fasta:
            if line.startswith('>'):
                if name is not None:
                    yield name, seq
                name = line[1:].rstrip()
                seq = ''
            else:
                seq += line.rstrip()
    yield name, seq


if False:
    def read_aa_matrices(path):
        data = {}
        entry_name = None
        mrow = None

        with open(path, 'rt') as f:
            for line in f:
                line = line.rstrip()
                if line[0] == 'H': # matrix name
                    assert entry_name is None
                    _, entry_name = line.split()
                elif line[0] == 'M': # matrix preamble
                    assert line == 'M rows = ARNDCQEGHILKMFPSTWYV, cols = ARNDCQEGHILKMFPSTWYV'
                    rows = 'ARNDCQEGHILKMFPSTWYV'
                    cols = 'ARNDCQEGHILKMFPSTWYV'
                    mrow = 0
                    mdata = {}
                elif line == '//': # end of matrix
                    data[entry_name] = mdata
                    entry_name = None
                    mrow = None
                elif mrow is not None: # matrix body
                    for mcol, value in enumerate(line.split()):
                        k = rows[mrow], cols[mcol]
                        mdata[k] = float(value)
                        if k[0] != k[1]:
                            mdata[k[::-1]] = mdata[k]
                    mrow += 1
        return data


def read_aa_data(path):
    data = {}
    state = 'start'

    with open(path, 'rt') as f:
        lines = (l.rstrip() for l in f)

        while True:
            if state == 'start':
                try: # new entry
                    line = next(lines)
                    assert line[0] == 'H'
                    _, entry_name = line.split()
                    state = 'header'
                except StopIteration: # end of file
                    break
            elif state == 'header':
                for line in lines:
                    if line[0] == 'M': # matrix preamble
                        assert line == 'M rows = ARNDCQEGHILKMFPSTWYV, cols = ARNDCQEGHILKMFPSTWYV'
                        rows = 'ARNDCQEGHILKMFPSTWYV'
                        cols = 'ARNDCQEGHILKMFPSTWYV'
                        state = 'matrix_data'
                    elif line[0] == 'I': # vector header
                        cols = list(zip(*[dc.split('/') for dc in line.split()[1:]]))
                        state = 'vector_data'
                    if state != 'header':
                        entry_data = {}
                        break
            elif state in {'matrix_data', 'vector_data'}:
                for row, line in enumerate(lines):
                    if line == '//': # end of data
                        data[entry_name] = entry_data
                        state = 'start'
                        del cols, entry_name, entry_data
                        break
                    #line_cols = cols if 
                    values = line.split()

                    # consistency checks on the number of values per row
                    if state == 'matrix_data':
                        if row == 0: # check if 
                            triangular = len(values) == 1
                        assert len(values) == (row + 1 if triangular else len(cols))
                    elif state == 'vector_data':
                        assert len(values) == len(cols[row])

                    # data parsing
                    for col, value_str in enumerate(values):
                        value = float('nan' if value_str == 'NA' else value_str)
                        if state == 'matrix_data':
                            k = rows[row], cols[col]
                        elif state == 'vector_data':
                            k = cols[row][col]
                        assert k not in entry_data
                        entry_data[k] = value
                        if state == 'matrix_data' and triangular:
                            entry_data[k[::-1]] = value
    return data
