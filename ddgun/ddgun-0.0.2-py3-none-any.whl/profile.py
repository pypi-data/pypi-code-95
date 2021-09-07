from . import aa
import pandas
from warnings import warn


class Profile:
    '''Protein profile object.

    Position is 1-based.
    '''
    def __init__(self, path_or_file=None):
        self.profile = None
        if path_or_file is not None:
            self.load(path_or_file)

    def load(self, path_or_file):
        '''Load profile from table.'''
        aa1 = pandas.Index(aa.one_letter_codes)
        df = pandas.read_csv(path_or_file, sep=None, engine='python')  # python engine needed for automatic detection of separator

        # check columns
        missing_aa = aa1.difference(df.columns)
        if len(missing_aa) > 0:
            raise ValueError('Missing AA columns in profile table: ' + ', '.join(missing_aa))
        unknown_cols = df.columns.difference(aa1).difference(['POS', 'SEQ', '-'])
        if len(unknown_cols) > 0:
            warn("Found unknown columns in profile table: " + ", ".join(unknown_cols))

        # check position column if any
        if 'POS' in df.columns:
            if 'POS' != df.columns[0]:
                warn("Found 'POS' column in profile but not in first position")
            if (df['POS'].astype(int) - df['POS'] != 0).any():
                raise ValueError("Found 'POS' column in profile but it is not an integer")
            df = df.set_index('POS')

        # check for 0-based position
        if df.index[0] == 0:
            warn("Found zero-based positions, adding 1")
            df.index = df.index + 1
        df.index.name = 'POS'

        self.profile = df  # keep everything

    def write(self, path_or_file):
        self.profile.to_csv(path_or_file, sep=' ', index=True, float_format='%.6f')

    def from_msa(path):
        import gzip
        from collections import Counter
        self = Profile()

        # load MSA in psiblast format
        seqs = []
        with (gzip.open if path.endswith('.gz') else open)(path, 'rt') as f:
            for line in f:
                name, seq = line[:-1].split()
                seqs.append(seq)
        if seqs[0][0] == '-':
            seqs[0] = seqs[0][1:] # there is always a - at the beginning of the first sequence, discard it
        
        # count letters for each position of the main sequence
        counts = pandas.DataFrame([Counter(s[i] for s in seqs) for i, c in enumerate(seqs[0]) if c != '-']).fillna(0)
        assert len(counts == len(seqs[0]))
        
        # set 1-based position as the index
        counts.index = pandas.Index(range(1, len(counts) + 1), name='POS')

        # check amino acid codes 
        output_cols = aa.one_letter_codes + ['-']
        possible_cols = set(output_cols) | set(aa.one_letter_ambiguity_codes.keys())
        too_many_cols = set(counts.columns) - possible_cols
        if too_many_cols:
            raise ValueError('Found unknown amino acid codes in MSA: "' + '", "'.join(too_many_cols) + '"')
        too_few_cols = set(output_cols) - set(counts.columns)
        if too_few_cols:
            raise ValueError('Missing amino acid codes in MSA: "' + '", "'.join(too_few_cols) + '"')
        
        # distribute ambiguity code counts to the single AAs
        for from_code, to_codes in aa.one_letter_ambiguity_codes.items():
            if from_code in counts.columns:
                for to_code in to_codes:
                    counts[to_code] += counts[from_code] / len(to_codes)
                del counts[from_code]
        assert set(counts.columns) == set(output_cols)
    
        freqs = counts / len(seqs)
        freqs['SEQ'] = list(seqs[0])
        self.profile = freqs.loc[:, output_cols + ['SEQ']]  # reorder columns
        return self

    def get_context(self, pos: int, context: int):  # position is based on table index
        '''Extract local subset of profile.

        profile: protein profile as pandas DataFrame
        pos: protein position
        context: number of positions to add around pos
        '''

        idx = list(range(pos - context, pos + context + 1))
        return self.profile.reindex(index=idx, columns=aa.one_letter_codes, fill_value=0).values.flatten()
