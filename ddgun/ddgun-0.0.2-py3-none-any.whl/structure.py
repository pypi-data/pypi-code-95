from Bio.PDB import PDBParser, PPBuilder


pdb_path='../tests/2ocj.pdb'
chain = 'A'
from Bio.PDB import PDBParser, PPBuilder
gstructure = PDBParser().get_structure('X', pdb_path)
structure = gstructure[0][chain]
pp = PPBuilder().build_peptides(structure, aa_only=False)
class Object:
    pass
self = Object()
self.structure = structure

def test_structure(pdb_path, chain):
    s = Structure(pdb_path, chain)
    seq = s.get_sequence()
    d = s.get_drenum_seq2pdb()
    d1 = s.get_drenum('2PDB')

class Structure:
    def __init__(self, pdb_path, chain):
        gstructure = PDBParser().get_structure('X', pdb_path)
        self.structure = gstructure[0][chain]
        self.peptides = PPBuilder().build_peptides(self.structure, aa_only=False)

    def get_sequence(self):
        return ''.join(str(ppc.get_sequence()) for ppc in self.peptides)

    def get_drenum_seq2pdb(self):
        d = {}
        i = 1
        for residue in self.structure:
            t, n, lab = residue.get_id()
            if t == ' ': # this is the only difference that i can see to
                         # get_drenum
                d[str(i)] = str(n) + lab.strip()
                i += 1
        return d
            
    def get_drenum(self, val):
        ''' Returns dict. key: seq_pos; value: pdb_pos'''
        reslist = []
        for ppc  in self.peptides:
            reslist += [res for res in ppc]

        pdb_pos = [str(r.get_id()[1]) + r.get_id()[2].strip() for r in reslist],
        seq_pos = map(str, range(1, len(reslist) + 1)) # profile position

        if val == "2PDB":
            return dict(zip(seq_pos, pdb_pos))
        elif val == "2SEQ":
            return dict(zip(pdb_pos, seq_pos))
        else:
            raise ValueError(f'bad val: {val}')
