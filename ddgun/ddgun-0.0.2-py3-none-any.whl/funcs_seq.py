from . import aa
AA = 'ARNDCQEGHILKMFPSTWYV'

def hydroScore(sm, prof, pos, w, m):
	return sm[m]*prof.iloc[pos][m]-sm[w]*prof.iloc[pos][w]

def evolScore(sm,prof,pos,w,m):
	return sum(prof.iloc[pos][a]*(sm[a,m] - sm[a,w]) for a in AA)

def potential_str(pot,prof,pos,w,m,lneighbp):
	ps = 0.0
	for i in lneighbp:
	 for a in AA:
		 ps -= prof.iloc[i][a]*(pot[m,a]- pot[w,a])
	return ps

def potential(pot, prof, pos, w, m, hw=2):
	context = range(max(0, pos - hw), min(len(prof), pos + hw + 1))
	return sum(prof.iloc[i][a]*(pot[w,a] - pot[m,a]) for i in context for a in AA if i != pos)
			
def hydroScore1(sub, prof, mat):
	w, m, p = sub.aa_from, sub.aa_to, sub.aa_pos
	return mat[m]*prof.at[p, m] - mat[w]*prof.at[p, w]

def evolScore1(sub, prof, mat):
	w, m, p = sub.aa_from, sub.aa_to, sub.aa_pos
	return sum(prof.at[p, a]*(mat[a, m] - mat[a, w]) for a in aa.one_letter_codes)

def potential1(sub, prof, mat, context=2):
	w, m, p = sub.aa_from, sub.aa_to, sub.aa_pos
	context = range(max(0, p - context), min(len(prof), p + context + 1))
	return sum(prof.at[i, a]*(mat[w, a] - mat[m, a]) for i in context for a in aa.one_letter_codes if i != p)


if False:
	def potential_str_score(pot,prof,seq,pos,w,m,neighblist):
			lneighb_pos=[]
			for v in neighblist:
					vaa,vpos=v[0],int(v[1:])
					lneighb_pos.append(int(v[1:]))
					assert vaa == seq[vpos-1]
			ps = potential_str(pot,prof,pos,w,m,lneighb_pos) # structural neighbors
			return ps

def extract_SEQscores(w, m, pos, prof, potseq, sm, kd):
	s = evolScore(sm, prof, pos, w, m)                # Blosum
	hs = hydroScore(kd, prof, pos, w, m)              # Hydrophobicity
	psseq = potential(potseq, prof, pos, w, m, hw=2)  # sequence neighbors
	return s, hs, psseq

def extract_SEQscores1(substitution, profile, potseq, sm, kd):
	prof = profile.profile
	s = evolScore1(substitution, prof, sm)                     # Blosum
	hs = hydroScore1(substitution, prof, kd)                   # Hydrophobicity
	psseq = potential1(substitution, prof, potseq, context=2)  # sequence neighbors
	return s, hs, psseq

def extract_3Dscores(w,m,pos,seq,prof,pot3d,sm,vScore,neighblist):
    ''' '''
    #assert seq[pos-1] == w # Togliere: non vale per le inverse!
    lneighb_pos=[]
    for v in neighblist:
        vaa,vpos=v[0],int(v[1:])
        lneighb_pos.append(vpos)
        #print vaa,vpos, vpos-1, seq[vpos-1]
        assert seq is None or vaa == seq[vpos-1]
    # structural neighbors: Bastolla-Vendruscolo potential
    psstr = potential_str(pot3d,prof,pos,w,m,lneighb_pos)
    return psstr

def combine_scores_seq(seq_blos,seq_hydro,seq_pot):
    return 0.3*seq_blos + 0.27*seq_hydro + 0.43*seq_pot 

def combine_scores_3d(seq_blos, seq_hydro, seq_pot, pot_3d, ac):
    return (seq_blos*0.20 + seq_pot*0.29 + seq_hydro*0.18 + pot_3d*0.33)*(1.1 - ac)

