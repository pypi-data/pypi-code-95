from nanofilm.__atom__ import AtomType,Atom
from math import cos,sin,radians,inf
from copy import deepcopy
from nanofilm.__exception__ import BasicException
import os.path

class Molecule:
    __currmolid__=0   # ID available for a new molecule
    
    def __init__(self,moltype,filename="",atomlist=[]):
        '''
        __init__(moltype,filename,atomlist) -> class constructor.

        Parameters
        ----------
        moltype : string
            A label allowing you to identify the type of the molecule, for 
            instance, "benzene" or "C6H12".
        filename : string, optional
            Name of an XYZ file containing the molecule structure. The default 
            is "".
        atomlist : Python list, optional
            List of Atom objects to be added to the molecule. The default is [].

        Returns
        -------
        None.
        '''
        if isinstance(moltype,str) and len(moltype)>0:
            self.moltype=moltype
        else:
            raise MoleculeError("'moltype' must be a string!")
            
            self.__del__()
        
        self.atoms=[]   # List of Atom objects that constitute the molecule
        self.atomtypes=[]   # List of atomic species found in the molecule
        self.com=[]     # List of the components of molecule's center of mass
        self.maxx=self.maxy=self.maxz=-inf  # Maximum Cartesian coordinates
        self.minx=self.miny=self.minz=inf   # Minimum Cartesian coordinates
        
        if len(filename)>0:
            if isinstance(filename,str):
                self.read_xyz(filename)
            else:
                raise MoleculeError("'filename' must be a valid file name!")
            
                self.__del__()
            
        if len(atomlist)>0:
            if isinstance(atomlist,list):
                for atom in atomlist:
                    self.add_atom(atom)
                    
                    if not atom.symbol in self.atomtypes:
                        self.atomtypes.append(atom.symbol)
            else:
                raise MoleculeError("'atomlist' must be a non-empyt list!")
            
                self.__del__()
                
        self.id=Molecule.__currmolid__
        Molecule.__currmolid__+=1

    def add_atom(self,atom):
        '''
        add_atom(atom) -> adds an atom to the molecule.

        Parameters
        ----------
        atom : Atom object
            New atom added to the molecule.

        Returns
        -------
        None.
        '''
        if isinstance(atom,Atom):
            self.atoms.append(atom)
            
            if not atom.symbol in self.atomtypes:
                self.atomtypes.append(atom.symbol)
            
            if len(self.atoms)==1:
                self.maxx=atom.x[0]
                self.minx=atom.x[0]
                self.maxy=atom.x[1]
                self.miny=atom.x[1]
                self.maxz=atom.x[2]
                self.minz=atom.x[2]
            else:
                if atom.x[0]>self.maxx:
                    self.maxx=atom.x[0]
                elif atom.x[0]<self.minx:
                    self.minx=atom.x[0]
                
                if atom.x[1]>self.maxy:
                    self.maxy=atom.x[1]
                elif atom.x[1]<self.miny:
                    self.miny=atom.x[1]
                
                if atom.x[2]>self.maxz:
                    self.maxz=atom.x[2]
                elif atom.x[2]<self.minz:
                    self.minz=atom.x[2]
        else:
            raise MoleculeError("'atom' must be an Atom object!")

            return

        self.__calc_com__()
            
    def remove_atom(self,atomid):
        '''
        remove_atom(atomid) -> removes an atom from the molecule.

        Parameters
        ----------
        index : int
            ID of the atom to be removed.

        Returns
        -------
        None.
        '''
        if isinstance(atomid,int) and atomid>=0 and atomid<Atom.__curratomid__:
            for i in range(len(self.atoms)):
                if self.atoms[i].id==atomid:
                    self.atoms.pop(i)
                    
                    break
        else:
            raise MoleculeError("'atomid' must be an integer greater than or equal to zero!")
            
            return
        
        self.__calc_com__()
        self.__get_extremes__()

    def read_xyz(self,filename):
        '''
        read_xyz(filename) -> reads the structure of the molecule from a file
            in XYZ format.

        Parameters
        ----------
        filename : string
            Name of the XYZ file.

        Returns
        -------
        None.
        '''        
        with open(filename,"r") as f:
            lines=f.readlines()

        for line in lines:
            l=line.split()
        
            if len(l)>=4:
                for atomtype in AtomType.__AtomTypes__:
                    if l[0]==atomtype.symbol:
                        self.atoms.append(Atom(atomtype,x=[float(l[1]),
                                                           float(l[2]),
                                                           float(l[3])]))
                        
                        if not atomtype.symbol in self.atomtypes:
                            self.atomtypes.append(atomtype.symbol)

                        break

        self.__calc_com__()
        self.__get_extremes__()
        
    def write_xyz(self,filename="molecule.xyz"):
        '''
        write_xyz(filename) -> saves the atomic coordinates of the molecule
            into an XYZ file.

        Parameters
        ----------
        filename : string, optional
            Name of the XYZ file. The default is "molecule.xyz".

        Returns
        -------
        None.
        '''
        with open(filename,"w") as f:
            f.write("%d\n\n" % (len(self.atoms)))
            
            for atom in self.atoms:
                f.write("%s %.6f %.6f %.6f\n" % (atom.symbol,atom.x[0],
                                                 atom.x[1],atom.x[2]))
                
    def write_pw_input(self,filename="molecule.in",vacuum=10.0,**kwargs):
        '''
        write_pw_input(filename,vacuum,**kwargs) -> creates a basic input file
            for geometry relaxation of the molecule using the pw.x code in the 
            Quantum Espresso package.

        Parameters
        ----------
        filename : string, optional
            Name of the input file. The default is "molecule.in".
        vacuum : float, optional
            Vacuum size separating the molecule from its images in all 
            directions. The default is 10.0 angstroms.
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
                    types in the molecule. The default is 1.0 Bohr magneton 
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
        celldm=self.maxx-self.minx+vacuum
        inpstr+="    celldm(1)=%.4f,\n" % (celldm*1.8897259886)
        inpstr+="    nat=%d,\n" % (len(self.atoms))
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
        inpstr+="1.0000   0.0000   0.0000\n"
        inpstr+="0.0000   %.4f   0.0000\n" % ((self.maxy-self.miny+vacuum)
                                              /celldm)
        inpstr+="0.0000   0.0000   %.4f\n" % ((self.maxz-self.minz+vacuum)
                                              /celldm)
        inpstr+="K_POINTS gamma\n"
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
        
        for atom in self.atoms:                    
            inpstr+="%s %.6f %.6f %.6f %d %d %d\n" % (atom.symbol,
                                                      atom.x[0],
                                                      atom.x[1],
                                                      atom.x[2],
                                                      int(not(atom.fixed[0])),
                                                      int(not(atom.fixed[1])),
                                                      int(not(atom.fixed[2])))
            
        with open(filename,"w") as f:
            f.write(inpstr)

    def move_molecule_to(self,x=[0.0,0.0,0.0]):
        '''
        move_molecule_to(x) -> rigidly moves the molecule such that its 
            center of mass will be located at 'x'.

        Parameters
        ----------
        x : Python list, optional
            New position of the molecule's center of mass. The default is 
            [0.0,0.0,0.0].

        Returns
        -------
        None.
        '''
        if isinstance(x,list) and len(x)==3:
            if isinstance(x[0],(float,int)) and isinstance(x[1],(float,int))\
                and isinstance(x[2],(float,int)):
                disp=[0.0,0.0,0.0]
                disp[0]=x[0]-self.com[0]
                disp[1]=x[1]-self.com[1]
                disp[2]=x[2]-self.com[2]
        
                self.displace_molecule(disp)
            else:
                raise MoleculeError("The components of 'x' must be numbers!")
                
                return
        else:
            raise MoleculeError("'disp' must be a list with three components!")
            
            return
        
    def displace_molecule(self,disp=[0.0,0.0,0.0]):
        '''
        displace_molecule(disp) -> rigidly displaces the molecule.

        Parameters
        ----------
        disp : Python list, optional
            Displacement vector. The default is [0.0,0.0,0.0].

        Returns
        -------
        None.

        '''
        if isinstance(disp,list) and len(disp)==3:
            if isinstance(disp[0],(float,int)) and isinstance(disp[1],(float,int))\
                and isinstance(disp[2],(float,int)):
                for atom in self.atoms:
                    atom.x[0]+=disp[0]
                    atom.x[1]+=disp[1]
                    atom.x[2]+=disp[2]

                self.com[0]+=disp[0]
                self.com[1]+=disp[1]
                self.com[2]+=disp[2]
                self.maxx+=disp[0]
                self.minx+=disp[0]
                self.maxy+=disp[1]
                self.miny+=disp[1]
                self.maxz+=disp[2]
                self.minz+=disp[2]
            else:
                raise MoleculeError("The components of 'disp' must be numbers!")
                
                return
        else:
            raise MoleculeError("'disp' must be a list with three components!")
            
            return

    def rotate_molecule(self,theta=0.0,phi=0.0,psi=0.0):
        '''
        rotate_molecule(theta,phi,psi) -> rotates the molecule around its
            center of mass.

        Parameters
        ----------
        theta : float, optional
            First Euler angle, in degrees. The default is 0.0.
        phi : float, optional
            Second Euler angle, in degrees. The default is 0.0.
        psi : float, optional
            Third Euler angle, in degrees. The default is 0.0.

        Returns
        -------
        None.
        '''
        if isinstance(theta,(float,int)) and isinstance(phi,(float,int))\
            and isinstance(psi,(float,int)):       
            theta=radians(theta)
            phi=radians(phi)
            psi=radians(psi)
        else:
            raise MoleculeError("Euler angles must be provided as numbers!")
            
            return
            
        a11=cos(theta)*cos(psi)
        a12=-cos(phi)*sin(psi)+sin(phi)*sin(theta)*cos(psi)
        a13=sin(phi)*sin(psi)+cos(phi)*sin(theta)*cos(psi)
        a21=cos(theta)*sin(psi)
        a22=cos(phi)*cos(psi)+sin(phi)*sin(theta)*sin(psi)
        a23=-sin(phi)*cos(psi)+cos(phi)*sin(theta)*sin(psi)
        a31=-sin(theta)
        a32=sin(phi)*cos(theta)
        a33=cos(phi)*cos(theta)
        
        for atom in self.atoms:
            x1=(atom.x[0]-self.com[0])
            y1=(atom.x[1]-self.com[1])
            z1=(atom.x[2]-self.com[2])
            x2=x1*a11+y1*a12+z1*a13
            y2=x1*a21+y1*a22+z1*a23
            z2=x1*a31+y1*a32+z1*a33
            atom.x[0]=x2+self.com[0]
            atom.x[1]=y2+self.com[1]
            atom.x[2]=z2+self.com[2]
            
        self.__get_extremes__()
                    
    def center_molecule(self):
        '''
        center_molecule() -> displaces the molecule such that its center of
            mass will be located at [0.0,0.0,0.0].

        Returns
        -------
        None.
        '''
        for atom in self.atoms:
            atom.x[0]-=self.com[0]
            atom.x[1]-=self.com[1]
            atom.x[2]-=self.com[2]
        
        self.maxx-=self.com[0]
        self.minx-=self.com[0]
        self.maxy-=self.com[1]
        self.minx-=self.com[1]
        self.maxz-=self.com[2]
        self.minz-=self.com[2]
        self.com=[0.0,0.0,0.0]
        
    def duplicate_molecule(self):
        '''
        duplicate_molecule() -> returns a copy of the current Molecule object.

        Returns
        -------
        Molecule object
            Copy of the molecule.
        '''
        newmol=deepcopy(self)
        newmol.id=Molecule.__currmolid__
        Molecule.__currmolid__+=1
        
        return newmol

    def __calc_com__(self):
        '''
        __calc_com__() -> sets the molecule's center of mass.

        Returns
        -------
        None.
        '''
        if len(self.atoms)>0:
            X=Y=Z=0.0
            totmass=0.0
        
            for atom in self.atoms:
                totmass=totmass+atom.atomicmass
                X+=atom.atomicmass*atom.x[0]
                Y+=atom.atomicmass*atom.x[1]
                Z+=atom.atomicmass*atom.x[2]

            if totmass>0.0:
                self.com=[X/totmass,Y/totmass,Z/totmass]
        else:
            raise MoleculeError("No atoms in the molecule!")
            
            return
            
    def __get_extremes__(self):
        '''
        __get_extremes__() -> gets the extreme coordinates of the molecule in 
            all directions.

        Returns
        -------
        None.
        '''
        natoms=len(self.atoms)
        
        if natoms==0:
            return
        elif natoms==1:
                self.maxx=self.atoms[0].x[0]
                self.minx=self.atoms[0].x[0]
                self.maxy=self.atoms[0].x[1]
                self.miny=self.atoms[0].x[1]
                self.maxz=self.atoms[0].x[2]
                self.minz=self.atoms[0].x[2]
        else:
            for atom in self.atoms:
                if atom.x[0]>self.maxx:
                    self.maxx=atom.x[0]
                elif atom.x[0]<self.minx:
                    self.minx=atom.x[0]
                
                if atom.x[1]>self.maxy:
                    self.maxy=atom.x[1]
                elif atom.x[1]<self.miny:
                    self.miny=atom.x[1]
                
                if atom.x[2]>self.maxz:
                    self.maxz=atom.x[2]
                elif atom.x[2]<self.minz:
                    self.minz=atom.x[2]
            
    def __del__(self):
        '''
        __del__() -> class destructor

        Returns
        -------
        None.
        '''
        pass
    
class MoleculeError(BasicException):
    pass