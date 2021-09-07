# aaindexN vengono da https://www.genome.jp/ftp/db/community/aaindex/
from . import funcs_seq
from . import funcs_3d
from . import utils # FIXME maybe read_fasta is not needed anymore

import pandas

from pkg_resources import resource_filename # FIXME read that we should use importlib.resources but I cannot get it to work
#import importlib.resources
#with importlib.resources.path(__package__, 'data/index1') as x:

def get_data(filename):
	#print(f"{filename} -> " + resource_filename(__package__, "data/" + filename))
	return resource_filename(__package__, "data/" + filename)

kd = utils.read_aa_data(get_data('aaindex1'))['KYTJ820101'] # Kyte-Doolittle Hydropathy index
pot1 = utils.read_aa_data(get_data('aaindex3'))['SKOJ970101'] # Skolnick
sMat = utils.read_aa_data(get_data('aaindex2'))['HENS920102'] # Blosum62

pot2 = utils.read_aa_data(get_data('aaindex3'))['BASU010101'] # Skolnick
#pot2 = funcs_seq.getPairMatrices(potfile)['BASU010101']

aa_table = pandas.read_csv(get_data('amino_acids.tsv'), sep='\t', names=['full', '3-letter', '1-letter'])
aa3to1 = aa_table.set_index('3-letter')['1-letter']


import re
aa1 = '|'.join(aa_table['1-letter'])
aa3 = '|'.join(aa_table['3-letter'])
aa1_re = re.compile(f"({aa1})([0-9]+)({aa1})")
aa3_re = re.compile(f"({aa3})([0-9]+)({aa3})")
def parse_aa_change(s):
	#if s.startswith('p.')
	m = aa1_re.fullmatch(s) or aa3_re.fullmatch(s)
	if m is None:
		raise ValueError(f"could not convert string to amino acid substitution: '{s}'")
	aa_from, aa_pos, aa_to = m.groups()
	if aa_pos == '0':
		raise ValueError(f"invalid zero position in amino acid substitution: '{s}'")
	aa_pos = int(aa_pos) - 1
	if len(aa_from) == 3:
		aa_from = aa3to1.at[aa_from]
		aa_to = aa3to1.at[aa_to]
	return aa_from, aa_pos, aa_to

def ddgun_seq(substitution, profile):
	scores = funcs_seq.extract_SEQscores1(substitution, profile, pot1, sMat, kd)
	return funcs_seq.combine_scores_seq(*scores)

#ddgun.ddgun_3d(sub, profile, structure, chain, access)
def ddgun_3d(sub, profile_path, structure_path, chain, access_path): # TODO make this work
	w, m, i = sub.aa_from, sub.aa_to, str(sub.aa_pos)
	#aa_from, aa_pos, aa_to = sub 
	#w, m, i = aa_from, aa_to, aa_pos + 1 #FIXME aa_pos 0/1-based?
	structure_name = re.search('([0-9a-z]{4})\.pdb', structure_path).group(1)

	from .profile import Profile
	profile = Profile(profile_path)
	prof = profile.profile

	pfn = structure_path
	n = structure_name + chain

	d_seq2pdb = funcs_3d.get_drenum_seq2pdb(n, structure_path) # this is the structure
	#lmutsXpdbk=[]
	#for kvar,ddg in pD[n]: lmutsXpdbk.append(kvar) # no idea
	lmutsXpdbk = [[(w, i, m)]]

	d_intorno3d, dist_intorno3d = funcs_3d.get_intorno_seqpin_seqpout_fase_2(n,lmutsXpdbk,5.0,d_seq2pdb, structure_path)
	# Accessibiity File Name 1vqjA.dssp_parsed
	d_access = funcs_3d.get_accessibility_fromseqnum(n,lmutsXpdbk, access_path, d_seq2pdb)

	# Gets sequence scores: substitution_matrix, hydrophobicity, sequence_neighbour_potential
	#s_smat, s_hyd, s_spot = funcs_seq.extract_SEQscores1(sub, profile, pot1, sMat, 0.0)
	s_smat, s_hyd, s_spot = funcs_seq.extract_SEQscores1(sub, profile, pot1, sMat, kd)
	pos = i
	# Gets structure scores
	s3d1 = funcs_seq.extract_3Dscores(w,m,i, None,prof,pot2,sMat,0.0, d_intorno3d[(n,(w,pos,m))])
	rsac=float(d_access[(n,(w,pos,m))])/100 # relative solvent accessibility
	return funcs_seq.combine_scores_3d(s_smat, s_hyd, s_spot,s3d1,rsac)


