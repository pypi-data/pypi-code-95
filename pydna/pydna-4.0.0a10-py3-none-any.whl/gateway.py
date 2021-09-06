#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2013-2020 by Björn Johansson.  All rights reserved.
# This code is part of the Python-dna distribution and governed by its
# license.  Please see the LICENSE.txt file that should have been included
# as part of this package.

"""Assembly of sequences by Gateway recombination.

Given a list of sequences (Dseqrecords), all sequences are analyzed for
presence of att(P|B|L|R)N where N is 1,2,3 or 4.

A graph is constructed where the att sites form a nodes and
sequences separating att sites form edges.

The NetworkX package is used to trace linear and circular paths through the
graph.
"""
from Bio.SeqFeature import ExactPosition as _ExactPosition
from Bio.SeqFeature import FeatureLocation as _FeatureLocation
from Bio.SeqFeature import CompoundLocation as _CompoundLocation
from pydna.utils import rc as _rc
from pydna.utils import memorize as _memorize
from pydna._pretty import pretty_str as _pretty_str
from pydna.contig import Contig as _Contig
from pydna.common_sub_strings import common_sub_strings
from pydna.dseqrecord import Dseqrecord as _Dseqrecord
import networkx as _nx
from copy import deepcopy as _deepcopy
import itertools as _itertools
import logging as _logging

_module_logger = _logging.getLogger("pydna." + __name__)

ambiguous_dna_regex = {
    "A": "T",
    "C": "G",
    "G": "C",
    "T": "A",
    "M": "[ACM]",
    "R": "[AGR]",
    "W": "[ATW]",
    "S": "[CGS]",
    "Y": "[CTY]",
    "K": "[GTK]",
    "V": "[ACGVMSR]",
    "H": "[ACTHMYW]",
    "D": "[AGTDRWK]",
    "B": "[CGTBSKY]",
    "X": "X",
    "N": "[ACGTBDHKMNRSVWY]" }

atts = """
attP1 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTACAAA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG CMASTWT AAAGYWG
attP2 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTACAAG AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG CMASTWT AAAGYWG
attP3 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATAAT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG CMASTWT AAAGYWG
attP4 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATAGA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG CMASTWT AAAGYWG
attP5 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATACA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG CMASTWT AAAGYWG

attB1 CMASTWT GTACAAA AAAGYWG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attB2 CMASTWT GTACAAG AAAGYWG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attB3 CMASTWT GTATAAT AAAGYWG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attB4 CMASTWT GTATAGA AAAGYWG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attB5 CMASTWT GTATACA AAAGYWG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG

attR1 CMASTWT GTACAAA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWG
attR2 CMASTWT GTACAAG AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWG
attR3 CMASTWT GTATAAT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWG
attR4 CMASTWT GTATAGA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWG
attR5 CMASTWT GTATACA AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT AAAGYWG

attL1 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTACAAA AAAGYWG CMASTWT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attL2 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTACAAG AAAGYWG CMASTWT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attL3 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATAAT AAAGYWG CMASTWT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attL4 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATAGA AAAGYWG CMASTWT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
attL5 AAATAATGATTTTATTTTGACTGATAGTGACCTGTTCGTTGCAACAMATTGATRAGCAATKMTTTYTTATAATGCCMASTTT GTATACA AAAGYWG CMASTWT AAAGYWGAACGAGAAACGTAAAATGATATAAATATCAATATATTAAATTAGATTTTGCATAAAAAACAGACTACATAATRCTGTAAAACACAACATATSCAGTCAYWWTG
"""


retable = str.maketrans(ambiguous_dna_regex)

for line in (line for line in atts.splitlines() if line.strip()):
    name, *parts = line.split()
    for part in parts:
        part.translate(retable)

class _Memoize(type):
    @_memorize("pydna.gateway.Gateway")
    def __call__(cls, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class Gateway(object, metaclass=_Memoize):
    """Assembly of linear DNA fragments into linear or circular constructs.

    The Assembly is meant to replace the Assembly method as it
    is easier to use. Accepts a list of Dseqrecords (source fragments) to
    initiate an Assembly object. Several methods are available for analysis
    of overlapping sequences, graph construction and assembly.

    Parameters
    ----------
    fragments : list
        a list of Dseqrecord objects.
    """

    def __init__(self, molecules=None):
        self.molecules =molecules
















































"""

https://blog.addgene.org/plasmids-101-cre-lox

https://en.wikipedia.org/wiki/Cre-Lox_recombination

13bp	      8bp	   13bp
ATAACTTCGTATA-NNNTANNN-TATACGAAGTTAT


Name	    13 bp  	        8 bp  	    13 bp
            Recognition     Spacer      Recognition
            Region          Region      Region

Wild-Type	ATAACTTCGTATA	ATGTATGC	TATACGAAGTTAT
lox511	    ATAACTTCGTATA	ATGTATaC	TATACGAAGTTAT
lox5171	    ATAACTTCGTATA	ATGTgTaC	TATACGAAGTTAT
lox2272	    ATAACTTCGTATA	AaGTATcC	TATACGAAGTTAT
M2	        ATAACTTCGTATA	AgaaAcca	TATACGAAGTTAT
M3	        ATAACTTCGTATA	taaTACCA	TATACGAAGTTAT
M7	        ATAACTTCGTATA	AgaTAGAA	TATACGAAGTTAT
M11	        ATAACTTCGTATA	cgaTAcca	TATACGAAGTTAT
lox71	    TACCGTTCGTATA	NNNTANNN	TATACGAAGTTAT
lox66	    ATAACTTCGTATA	NNNTANNN	TATACGAACGGTA

"""