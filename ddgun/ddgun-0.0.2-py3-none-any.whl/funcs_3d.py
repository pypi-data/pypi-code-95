import sys
import string
from Bio.PDB import *
from Bio.PDB.Polypeptide import three_to_one, is_aa


aa_modif={"TRN":"TRP", "CSO":"CYS","M3L":"LYS", "PCA":"GLU"}

if False:
    def testPos(structure,mut):
            ppb=PPBuilder()
            s=""
            for pp in ppb.build_peptides(structure):
                    s+=pp.get_sequence()
            w,pos,m=mut
            i=0
            ok=False
            for residue in structure:
                    t,n,lab=residue.get_id()
                    if t == ' ':
                            nt=str(n)+lab.strip()
                            if pos==nt:
                                    #print "XXXXXX",s, len(s),pos,i
                                    if s[i]==w:
                                            ok=True
                                            #print i+1,s[i],nt,structure[(' ',n,lab)].get_resname()
                            i+=1
            return ok

#def get_atomseq(structure):
#    ppb=PPBuilder()
#    s=""
#    for pp in ppb.build_peptides(structure):
#        s+=pp.get_sequence()
#    return s



#################################################################
##  Fnuctions to pass from sequence_numbering to pdb_numbering ##

def mk_d_renumb_KseqVpdb(structure):
        d={}
        ppb=PPBuilder()
        #s=""
        #for pp in ppb.build_peptides(structure):
        #        s+=pp.get_sequence()
        i=1
        for residue in structure:
                t,n,lab=residue.get_id()
                if t == ' ':
                        #d[(n,lab.strip())]=i
                        d[str(i)]=str(n)+lab.strip()
                        i+=1
        return d

def mk_d_renumb_KseqVpdb_onlyCA(structure):
        s,d="",{}
        for res in structure:
                a3=res.get_resname()
                if a3 in aa_modif.keys():
                                #a3=aa_modif[a3] # NO! SONO HETATM
                                pass
                else:
                                if is_aa(a3):
                                     #s+=three_to_one(res.get_resname()) # da errore in caso di non-residui o res-modif
                                     s+=three_to_one(a3)
        i=1
        for residue in structure:
                t,n,lab=residue.get_id()
                if t == ' ':
                        d[str(i)]=str(n)+lab.strip()
                        i+=1


def get_drenum_seq2pdb(pdbkcode,pdbfile):
    ''' Returns dict. key: seq_pos PIù CHE SEQ POS E' LA POSIZIONE DEL PROFILO- PARTE DA 1; value: pdb_pos'''
    chain=pdbkcode[-1]
    parser=PDBParser()
    structure=parser.get_structure('X',pdbfile)
    if pdbkcode[:-1].lower()=='1lrp':
        dpos=mk_d_renumb_KseqVpdb_onlyCA(structure[0][chain]) # FIXME why a specific function for one protein?
    else:
        dpos=mk_d_renumb_KseqVpdb(structure[0][chain])
    return dpos


def invert_keyval(din): #inverte un dizionario (da usare per fare seq:pdb->pdb:seq)
    do={}
    for kin in din: do[din[kin]]=kin
    return do


if False:
    def renum_muts(oldmut,diz):
            newmut=[]
            for ele in oldmut.split(','):
                         a,b,c=ele[0],ele[1:-1],ele[-1]
                         newmut.append(a+diz[b]+c)
            newmut=','.join(newmut)
            return newmut
#################################################################




##########################################################################################################
def get_neighb_fase2(name,structure,lpos,radius_angst):
    model = structure[0]
    chain = model[name[4]]
    # Next line: A for atoms # ho dato la catena e non la struttura x avere solo i vicnini di quella catena
    all_atom_list = Selection.unfold_entities(chain, 'A')
    ns = NeighborSearch(all_atom_list)
    dv={}
    dist = {} #dizionario con tutte le distanze pesate
    for pos in lpos:
       dv[pos]=[]
       dist[pos] = []
       try: p,rlabel=int(pos),' '
       except: p,rlabel=int(pos[:-1]),pos[-1]
       for atomo in chain[(' ',p,rlabel)]: # for atomo in chain[p]:
           rvicini = ns.search(atomo.get_coord(), radius_angst, "R")
           for aa in rvicini:
                lista_distanze = []
                if aa.get_id()[0]==' ':
                    if aa.get_id()[1]!=p:
                        for atoms in aa:
                            lista_distanze.append(atomo-atoms)
                        if aa not in dv[pos]: 
                            dv[pos].append(aa)  # Returns object
                            dist[pos].append((aa, min(lista_distanze)))
                        else:
                            for bb in dist[pos]:
                                if bb[0] == aa:
                                    if min(lista_distanze) < bb[1]:
                                        dist[pos].remove(bb)
                                        dist[pos].append((aa, min(lista_distanze)))
                         # Following line: Returns 1letter_aa+position
                         #if aa not in dv[pos]: dv[pos].append(three_to_one(aa.get_resname())+str(aa.get_id()[1])+aa.get_id()[2])
    return dv, dist
    
    
def get_neighb(name,structure,lpos,radius_angst):
    ''' Takes pdb numberig and returns bio.pdb residue objects (pdb-numbering)'''
    '''Output: {'0': [<Residue VAL het=  resseq=1 icode= >, <Residue LYS het=  resseq=140 icode= >, <Residue LEU het=  resseq=137 icode= >, <Residue LEU het=  resseq=2 icode= >, <Residue GLU het=  resseq=136 icode= >, <Residue LYS het=  resseq=133 icode= >]}'''
    model = structure[0]
    chain = model[name[4]]
    # Next line: A for atoms # ho dato la catena e non la struttura x avere solo i vicnini di quella catena
    all_atom_list = Selection.unfold_entities(chain, 'A')
    ns = NeighborSearch(all_atom_list)
    dv={}
    for pos in lpos:
           dv[pos]=[]
           try: p,rlabel=int(pos),' '
           except: p,rlabel=int(pos[:-1]),pos[-1]
           for atomo in chain[(' ',p,rlabel)]: # for atomo in chain[p]:
               centro = atomo.get_coord()
               rvicini = ns.search(centro, radius_angst, "R")
               for aa in rvicini:
                   if aa.get_id()[0]==' ':
                      if aa.get_id()[1]!=p:
                         if aa not in dv[pos]: dv[pos].append(aa)  # Returns object
                     # Following line: Returns 1letter_aa+position
                     #if aa not in dv[pos]: dv[pos].append(three_to_one(aa.get_resname())+str(aa.get_id()[1])+aa.get_id()[2])
    return dv


def get_intorno_seqpin_seqpout(k,lmuts,Cangstroms,d_seq2pdb_numb,pdbfname):
    '''Da seq a seq'''
    # Reads mutated positions for each pdb
    l_muts_pdb=[]
    for muts in lmuts:
        ll=[]
        for mut in muts: 
            ll.append((mut[0],d_seq2pdb_numb[mut[1]],mut[2]))
        ll=tuple(ll)
        l_muts_pdb.append(ll)

    d_pdb=get_intorno_pdbpin_pdbpout(k,l_muts_pdb,Cangstroms,pdbfname)
   
    dall={}
    d_pdb2seq_numb=invert_keyval(d_seq2pdb_numb)
    for n,mut in d_pdb.keys():
             mut_seqn=(mut[0],d_pdb2seq_numb[mut[1]],mut[2])
             dall[(n,mut_seqn)]=[]
             for wtpos in d_pdb[(n,mut)]:
                 wt=wtpos[0]
                 seqpos=d_pdb2seq_numb[wtpos[1:]]
                 dall[(n,mut_seqn)].append(wt+seqpos)
    return dall

def get_intorno_pdbpin_pdbpout(k,llmuts,Cangstroms,fname):
    ''' Input: k=pdb_code
               llmuts: list of mutations [ (('T','44','A'),('S','41','K')), ...]
               Cangstroms: radius (float)
               fname: name of the pdb structure/model file
    Output: dictionary with structural neighbours.
    It takes as input the pdb-numbring (pdbpin)
    and returns as output the pdb-numbering (pdbpout)'''
    '''output {('102mA', ('M', '0', 'A')): ['V1', 'K140', 'L137', 'L2', 'E136', 'K133']...}
    LA NUMERAZIONE E' PDB'''
    # Gets mutated positions
    l_mutpos=[]
    for muts in llmuts:
        for mut in muts:
            pdb_pos=mut[1]
            if pdb_pos not in l_mutpos: l_mutpos.append(pdb_pos)

    # Compute neighbor for mutated positions
    parser=PDBParser()
    structure=parser.get_structure('X',fname)
    dneigh=get_neighb(k,structure,l_mutpos,Cangstroms)

    # Makes a dict: {mutatedpos_pdbnum : [ neighbor1, neighbor2, ... ], ...}
    dout={}
    for muts in llmuts:
         for mut in muts:
             dout[(k,mut)]=[]
             ps=mut[1]
             for aa in dneigh[ps]:
                 pdbpos=(str(aa.get_id()[1])+aa.get_id()[2]).strip()
                 dout[(k,mut)].append(three_to_one(aa.get_resname())+pdbpos)
    return dout






def get_intorno_seqpin_seqpout_fase_2(k,lmuts,Cangstroms,d_seq2pdb_numb,pdbfname):
    '''Da seq a seq'''
    # Reads mutated positions for each pdb
    """gb interpretation:
k: pdb name + chain, e.g.: 2ocjA
lmuts: list of list of mutations (aa_from, aa_pos(str), aa_to) with seq-based position
Cangstroms: 5.0
d_seq2pdb_numb: seq to pdb position map
pdbfname: pdb file path
"""
    l_muts_pdb=[]
    for muts in lmuts:
        ll=[]
        for mut in muts: 
            ll.append((mut[0],d_seq2pdb_numb[mut[1]],mut[2]))
        ll=tuple(ll)
        l_muts_pdb.append(ll)
    d_pdb=get_intorno_pdbpin_pdbpout_fase2(k,l_muts_pdb,Cangstroms,pdbfname)
    dall, dist_all ={},{}
    d_pdb2seq_numb=invert_keyval(d_seq2pdb_numb)
    for n,mut in d_pdb.keys():
             mut_seqn=(mut[0],d_pdb2seq_numb[mut[1]],mut[2])
             dall[(n,mut_seqn)]=[]
             dist_all[(n,mut_seqn)]=[]
             for wtpos in d_pdb[(n,mut)]:
                 wt=wtpos[0][0]
                 seqpos=d_pdb2seq_numb[wtpos[0][1:]]
                 dall[(n,mut_seqn)].append(wt+seqpos)
                 dist_all[(n,mut_seqn)].append((wt+seqpos, wtpos[1]))
    return dall, dist_all
    
        

def get_intorno_pdbpin_pdbpout_fase2(k,llmuts,Cangstroms,fname):
    ''' Input: k=pdb_code
               llmuts: list of mutations [ (('T','44','A'),('S','41','K')), ...]
               Cangstroms: radius (float)
               fname: name of the pdb structure/model file
    Output: dictionary with structural neighbours.
    It takes as input the pdb-numbring (pdbpin)
    and returns as output the pdb-numbering (pdbpout)'''
    '''output {('102mA', ('M', '0', 'A')): ['V1', 'K140', 'L137', 'L2', 'E136', 'K133']...}
    LA NUMERAZIONE E' PDB'''
    # Gets mutated positions
    l_mutpos=[]
    for muts in llmuts:
        for mut in muts:
            pdb_pos=mut[1]
            if pdb_pos not in l_mutpos: l_mutpos.append(pdb_pos)
    # Compute neighbor for mutated positions
    parser=PDBParser()
    structure=parser.get_structure('X',fname)
    dneigh, dist =get_neighb_fase2(k,structure,l_mutpos, Cangstroms)
    # Makes a dict: {mutatedpos_pdbnum : [ neighbor1, neighbor2, ... ], ...}
    dout={}
    for muts in llmuts:
         for mut in muts:
             dout[(k,mut)]=[]
             ps=mut[1]
             for aa in dist[ps]:
                 pdbpos=(str(aa[0].get_id()[1])+aa[0].get_id()[2]).strip()
                 dout[(k,mut)].append((three_to_one(aa[0].get_resname())+pdbpos, round(aa[1], 2)))
    return dout



##########################################################################################################



######################################################################################
#######                  Function to retrieve accessibility                    #######

def get_accessibility_fromseqnum(pdbk,lmuts,accfname,drenum_s2p):

    """
    Requires: pdbk: 1aj3A 
            list of muts in the folo: [(('W', '13', 'Y'), ('S', '65', 'L'))]
            accfname: file-name
            drenum_s2p: dictionary from seq_numbering to pdb_numbering
    """
    # Reads dssp accessibility
    try:
      lines=open(accfname,'r').readlines()
    except:
      sys.stderr.write('cannot open file '+accfname+'\n')
      sys.exit()
    d_dssp={}
    for line in lines: d_dssp[line.split()[0]]=line.split()[1]

    # Makes dictionary: single_mutation : accessibility
    dout={}
    for muts in lmuts:
      for mut in muts:
          pdb_pos=drenum_s2p[mut[1]]
          if mut not in dout.keys(): dout[(pdbk,mut)]=int(d_dssp[pdb_pos])
    return dout

######################################################################################


