from nanofilm.__atom__ import AtomType
from nanofilm.__molecule__ import Molecule
from nanofilm.__lattice__ import Lattice
from nanofilm.__slab__ import Slab
from math import inf,sqrt
import os.path
from nanofilm.__exception__ import BasicException

class Film:
    def __init__(self):
        '''
        __init__() -> Class constructor.

        Returns
        -------
        None.
        '''
        self.slab=None
        self.molecules=[]
        self.atomtypes=[]
        self.mindistance=1.0
    
    def set_substrate(self,slab):
        '''
        set_substrate(slab) -> sets the substrate.

        Parameters
        ----------
        slab : Slab object
            Substrate.

        Returns
        -------
        None.
        '''
        if isinstance(slab,Slab):
            self.slab=slab
            
            for symbol in slab.atomtypes:
                if not symbol in self.atomtypes:
                    self.atomtypes.append(symbol)
        else:
            raise FilmError("'slab' must be a Slab object!")
            
            return
        
    def add_molecule(self,molecule,ads_site="",ads_site_index=-1,pos=[],
                     vert_sep=1.0):
        '''
        add_molecule(molecule,ads_site,ads_site_index,pos,vert_sep) -> adsorbs 
            a molecule onto the previously defined substrate.

        Parameters
        ----------
        molecule : Molecule object
            Adsorbed molecule.
        ads_site : string
            Label of the adsorption site. The default is "".
        ads_site_index : int, optional
            Index of an adsorption site on the substrate. The default is -1,
            which means that no adsorption site will be used.
        pos : Python list, optional
            Coordinates in the XY plane where the center of mass of the 
            molecule will be placed over. The default is [].
        vert_sep : float, optional
            Nearest vertical distance separating the molecule from the 
            substrate. The default is 1.0 (Angstrom).

        Returns
        -------
        None.
        '''       
        if self.slab is None:
            raise FilmError("No substrate has been defined!")
            
            return
        elif not isinstance(molecule,Molecule):
            raise FilmError("'molecule' must be a Molecule object!")
            
            return
        
        ads_site=str(ads_site)
        xnew=[0.0,0.0,0.0]
        
        if not isinstance(ads_site_index,int):
            raise FilmError("'ads_site_index' must be an integer!")
            
            return
        
        if (not isinstance(vert_sep,(int,float))) or vert_sep<=0.0:
            raise FilmError("'vert_sep' must be a number greater than zero!")
            
            return
        elif vert_sep<self.mindistance:
            vert_sep=self.mindistance
        
        if len(ads_site)>0 and (ads_site in self.slab.ads_sites.keys()) and\
            ads_site_index>=0 and ads_site_index<len(self.slab.ads_sites[ads_site]):
            xnew[0]=self.slab.ads_sites[ads_site][ads_site_index][0]
            xnew[1]=self.slab.ads_sites[ads_site][ads_site_index][1]
        elif len(pos)==2:
            xnew[0]=pos[0]
            xnew[1]=pos[1]
        else:
            raise FilmError("Either 'ads_site' and 'ads_site_index' or 'pos' must be properly set!")
            
            return
                   
        self.molecules.append(molecule)
        
        for symbol in molecule.atomtypes:
            if not symbol in self.atomtypes:
                self.atomtypes.append(symbol)
        
        zmin=self.slab.top+vert_sep
        dz=zmin-molecule.minz
        xnew[2]=molecule.com[2]+dz
                
        molecule.move_molecule_to(xnew)
        
    def remove_molecule(self,molid):
        '''
        remove_molecule(molid) -> removes an adsorbed molecule.

        Parameters
        ----------
        molid : int
            ID of the adsorbed molecule to be removed.

        Returns
        -------
        None.
        '''
        if isinstance(molid,int) and molid>=0 and molid<Molecule.__currmolid__:
            for i in range(len(self.molecules)):
                if self.molecules[i].id==molid:
                    self.molecules.pop(i)
                    
                    break
        else:
            raise FilmError("'molid' must be an integer greater than or equal to zero!")
            
            return
        
    def enforce_mindist(self,moltype=None,mindist=None):
        '''
        enforce_mindist(mindist) -> if necessary, displaces vertically a molecule
            such that the nearest separation of the molecule with respect to 
            the top of the substrate is the prescribed minimum distance.

        Parameters
        ----------
        moltype : string, optional
            Label identifying the molecule. The default is None.
        mindist : float, optional
            Minimum distance separating the molecule from the substrate. The 
            default is None.

        Returns
        -------
        None.
        '''
        if mindist is None or mindist<self.mindistance:
            mindist=self.mindistance
        else:
            if not isinstance(mindist,(float,int)):
                raise FilmError("'mindist' must be a number greater than zero!")
                
                return
        
        for molecule in self.molecules:
            if moltype is None or molecule.moltype==moltype:
                if molecule.minz-self.slab.top<mindist:
                    dispz=mindist-(molecule.minz-self.slab.top)
                
                    molecule.displace_molecule([0.0,0.0,dispz])
                
    def write_xyz(self,filename="film.xyz",vacuum=10.0):
        '''
        write_xyz(filename,vacuum) -> saves the atomic coordinates of the 
            adsorbed system into an XYZ file.

        Parameters
        ----------
        filename : string, optional
            Name of the XYZ file. The default is "film.xyz".
        vacuum : float, optional
            Height of the vacuum layer to be added to the top of the film. 
            The default is 10.0 (Angstroms).

        Returns
        -------
        None.
        '''
        maxz=-inf
        natoms=len(self.slab.atoms)
        
        for molecule in self.molecules:
            natoms+=len(molecule.atoms)
            
            if molecule.maxz>maxz:
                maxz=molecule.maxz
                
        with open(filename,"w") as f:
            f.write("%d\n" % natoms)
            f.write('Lattice="%.6f %.6f 0.0 %.6f %.6f 0.0 0.0 0.0 %.6f" Properties=species:S:1:pos:R:3\n' 
                    % (self.slab.lattice_vectors[0][0],
                       self.slab.lattice_vectors[0][1],
                       self.slab.lattice_vectors[1][0],
                       self.slab.lattice_vectors[1][1],
                       maxz+vacuum))
            
            for atom in self.slab.atoms:
                f.write("%s %.6f %.6f %.6f\n" % (atom.symbol,atom.x[0],
                                                 atom.x[1],atom.x[2]))
                
            for molecule in self.molecules:
                for atom in molecule.atoms:
                    f.write("%s %.6f %.6f %.6f\n" % (atom.symbol,atom.x[0],
                            atom.x[1],atom.x[2]))
                    
    def write_pw_input(self,filename="film.in",vacuum=20.0,**kwargs):
        '''
        write_pw_input(filename,vacuum,**kwargs) -> creates a basic input file
            for geometry relaxation of the film using the pw.x code in the 
            Quantum Espresso package.

        Parameters
        ----------
        filename : string, optional
            Name of the input file. The default is "film.in".
        vacuum : float, optional
            Vacuum size separating the top of the highest molecule from the
            bottom of the image of the slab. The default is 20.0 angstroms.
        **kwargs : Python dictionary.
            Dictionary containing key-value pairs that allow some customization 
            of the input file. At the moment, those are the keys accepted:
                ecutwfc: float, optional
                    Plane-wave energy cutoff. The default is 24.0 Ry.
                ecutrho: float, optional
                    Charge density cutoff. The default is 96.0 Ry.
                nspin: integer, optional
                    Spin polarization. It can be either 1 (non-polarized) or 
                    2 (polarized, magnetization along z axis). The default is 1.
                starting_magnetization : Python list, optional
                    List of starting magnetic moments for the different atom 
                    types in the system. The default is 1.0 Bohr magneton 
                    for the first atom type and 0.0 for the others, if any.
                input_dft : string, optional
                    It allows to activate non-local vdW interaction by setting
                    it to 'vdw-df'. The default is ''.
                mixing_mode : string ,optional
                    Mixing charge mode. It can be 'plain' (Broyden mixing),
                    'TF' (Thomas-Fermi screening for homogeneous systems) or
                    'local-TF' (local density Thomas-Fermi screening). The
                    default is 'plain'.
                mixing_beta : float, optional
                    Beta parameter in charge mixing. The default is 0.7.
                kvec : Python list, optional
                    Grid (first three elements) and shift (last three 
                    components) used to generate k-points according to the
                    Monhorst-Pack scheme. The default is [1,1,1,0,0,0].

        Returns
        -------
        None.
        '''        
        inpstr="&CONTROL\n"
        inpstr+="    calculation='relax',\n"
        inpstr+="    restart_mode='from_scratch',\n"
        inpstr+="    pseudo_dir='.',\n"
        inpstr+="    prefix='"+os.path.splitext(os.path.basename
                                                (filename))[0]+"',\n"
        inpstr+="    nstep=500,\n/\n"
        inpstr+="&SYSTEM\n"
        inpstr+="    ibrav=0,\n"
        celldm=sqrt(pow((self.slab.lattice_vectors[0][0]),2)+
                    pow((self.slab.lattice_vectors[0][1]),2))
        inpstr+="    celldm(1)=%.4f,\n" % (celldm*1.8897259886)
        maxz=-inf
        natoms=len(self.slab.atoms)
        
        for molecule in self.molecules:
            natoms+=len(molecule.atoms)
            
            if molecule.maxz>maxz:
                maxz=molecule.maxz
        
        inpstr+="    nat=%d,\n" % natoms
        inpstr+="    ntyp=%d,\n" % (len(self.atomtypes))
        
        if "ecutwfc" in kwargs:
            inpstr+="    ecutwfc=%.4f,\n" % kwargs["ecutwfc"]
        else:
            inpstr+="    ecutwfc=24.00,\n"
        
        if "ecutrho" in kwargs:
            inpstr+="    ecutrho=%.4f,\n" % kwargs["ecutrho"]
        else:
            inpstr+="    ecutrho=96.00,\n"
            
        if "nspin" in kwargs and kwargs["nspin"]==2:
            inpstr+="    nspin=2,\n"
            inpstr+="    occupations='smearing',\n"
            inpstr+="    smearing='gaussian',\n"
            inpstr+="    degauss=0.02,\n"
                
            if "starting_magnetization" in kwargs and \
                len(kwargs["starting_magnetization"])>0:
                    for i in range(len(kwargs["starting_magnetization"])):
                        if i<len(self.atomtypes):                           
                            inpstr+="    starting_magnetization(%d)=%.2f,\n" \
                                % (i+1,kwargs["starting_magnetization"][i])
                        else:
                            break
            else:
                inpstr+="    starting_magnetization(1)=1.00,\n"
        else:
            inpstr+="    nspin=1,\n"
            
        if "input_dft" in kwargs and kwargs["input_dft"]=="vdw-df":
            inpstr+="    input_dft='vdw-df',\n"
        
        inpstr+="/\n"
        inpstr+="&ELECTRONS\n"
        
        if "mixing_mode" in kwargs and (kwargs["mixing_mode"]=="TF" or\
            kwargs["mixing_mode"]=="local-TF"):
                inpstr+="    mixing_mode='%s',\n" % kwargs["mixing_mode"]
        else:
            inpstr+="    mixing_mode='plain',\n"
            
        if "mixing_beta" in kwargs and kwargs["mixing_beta"]>0.0:
            inpstr+="    mixing_beta=%.4f,\n" % kwargs["mixing_beta"]
        else:
            inpstr+="    mixing_beta=0.7,\n"
        
        inpstr+="    electron_maxstep=200,\n/\n"
        inpstr+="&IONS\n/\n"
        inpstr+="CELL_PARAMETERS alat\n"
        inpstr+="%.4f   %.4f   0.0000\n" % (self.slab.lattice_vectors[0][0]
                                            /celldm,
                                            self.slab.lattice_vectors[0][1]
                                            /celldm)
        inpstr+="%.4f   %.4f   0.0000\n" % (self.slab.lattice_vectors[1][0]
                                            /celldm,
                                            self.slab.lattice_vectors[1][1]
                                            /celldm)
        inpstr+="0.0000   0.0000   %.4f\n" % ((maxz+vacuum)/celldm)

        inpstr+="K_POINTS automatic\n"

        if "kvec" in kwargs and len(kwargs["kvec"])==6:
            inpstr+="%d %d %d %d %d %d\n" % (kwargs["kvec"][0],
                                             kwargs["kvec"][1],
                                             kwargs["kvec"][2],
                                             kwargs["kvec"][3],
                                             kwargs["kvec"][4],
                                             kwargs["kvec"][5])
        else:
            inpstr+="1 1 1 0 0 0\n"
        
        inpstr+="ATOMIC_SPECIES\n"
        
        for symbol in self.atomtypes:
            for atomtype in AtomType.__AtomTypes__:
                if atomtype.symbol==symbol:
                    if atomtype.pseudopotential=="":
                        pseudopotential=symbol+".UPF"
                    else:
                        pseudopotential=atomtype.pseudopotential
                    
                    inpstr+="%s %.4f %s\n" % (symbol,atomtype.atomicmass,
                                              pseudopotential)
                    
                    break
                
        inpstr+="ATOMIC_POSITIONS angstrom\n"
        
        for atom in self.slab.atoms:                    
            inpstr+="%s %.6f %.6f %.6f %d %d %d\n" % (atom.symbol,
                                                      atom.x[0],
                                                      atom.x[1],
                                                      atom.x[2],
                                                      int(not(atom.fixed[0])),
                                                      int(not(atom.fixed[1])),
                                                      int(not(atom.fixed[2])))
            
        for molecule in self.molecules:
            for atom in molecule.atoms:
                inpstr+="%s %.6f %.6f %.6f %d %d %d\n" % (atom.symbol,
                                                          atom.x[0],
                                                          atom.x[1],
                                                          atom.x[2],
                                                          int(not(atom.fixed[0])),
                                                          int(not(atom.fixed[1])),
                                                          int(not(atom.fixed[2])))
            
        with open(filename,"w") as f:
            f.write(inpstr)
                           
class FilmError(BasicException):
    pass