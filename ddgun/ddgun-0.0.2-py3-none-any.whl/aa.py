three_to_one_letter_codes = {
    'Cys': 'C', 'Asp': 'D', 'Ser': 'S', 'Gln': 'Q', 'Lys': 'K',
    'Ile': 'I', 'Pro': 'P', 'Thr': 'T', 'Phe': 'F', 'Asn': 'N',
    'Gly': 'G', 'His': 'H', 'Leu': 'L', 'Arg': 'R', 'Trp': 'W',
    'Ala': 'A', 'Val': 'V', 'Glu': 'E', 'Tyr': 'Y', 'Met': 'M'
}
three_letter_codes = sorted(three_to_one_letter_codes.keys())
one_letter_codes = sorted(three_to_one_letter_codes.values())

one_letter_ambiguity_codes = {
    'Z': ['E', 'Q'],
    'B': ['D', 'N'],
    'J': ['L', 'I'],
#    'O': ['K'],  # Pyrrolysine -> Lysine
    'U': ['C'],  # Selenocysteine -> Cysteine
    'X': one_letter_codes,
}

#aa3_pattern_str = '|'.join(aa3)
#hgvs_p_pattern_str = '(?P<prot_id>[^:]+):p.(?P<aa_from>' + aa3_pattern_str + ')(?P<aa_pos>[0-9]+)(?P<aa_to>' + aa3_pattern_str + ')'

class Substitution:  # FIXME only accepts one letter codes!
    '''Class representing an amino acid substitution'''
    def __init__(self, aa_from, aa_to, aa_pos):
        if aa_from not in one_letter_codes:
            raise ValueError(f'Bad amino acid code: {aa_from}')
        if aa_to not in one_letter_codes:
            raise ValueError(f'Bad amino acid code: {aa_to}')
        if aa_pos <= 0:
            raise ValueError(f'Position must be 1-based, bad value {aa_pos}')
        self.aa_from = aa_from
        self.aa_to = aa_to
        self.aa_pos = aa_pos

    def parse(s):
        return Substitution(aa_from=s[0], aa_to=s[-1], aa_pos=int(s[1:-1]))
    def __str__(self):
        return f"{self.aa_from}{self.aa_pos}{self.aa_to}"
