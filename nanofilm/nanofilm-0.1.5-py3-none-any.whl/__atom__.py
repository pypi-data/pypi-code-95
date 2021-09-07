from nanofilm.__exception__ import BasicException
from copy import deepcopy

class AtomType:
    __AtomTypes__=[]     # List of atom types
    
    def __init__(self,symbol,element,atomicnumber,atomicmass,
                 pseudopotential=""):
        '''
        __init__(symbol,element,atomicnumber,atomicmass,pseudopotential) ->
            class constructor.

        Parameters
        ----------
        symbol : string
            Symbol of the chemical element. For example, "C" for carbon.
        element : string
            Name of the atomic element. For example, "carbon".
        atomicnumber : int
            Atomic number of the element.
        atomicmass : float
            Atomic mass of the element, usually in atomic units.
        pseudopotential : string, optional
            Name of the file containing the pseudopotential for the element,
            to be employed in DFT calculations. The default is "".

        Returns
        -------
        None.
        '''
        if isinstance(symbol,str) and len(symbol)<=4 and len(symbol)>0:
            self.symbol=symbol
        else:
            raise AtomTypeError("'symbol' must be a string with up to 4 characters!")
            
            self.__del__()
        
        if isinstance(element,str) and len(element)>0:
            self.element=element
        else:
            raise AtomTypeError("'element' must be a string!")
            
            self.__del__()
        
        if isinstance(atomicnumber,int) and atomicnumber>0:
            self.atomicnumber=atomicnumber
        else:
            raise AtomTypeError("'atomicnumber' must be a positive integer!")
            
            self.__del__()
            
        if isinstance(atomicmass,(int,float)) and atomicmass>0.0:
            self.atomicmass=atomicmass
        else:
            raise AtomTypeError("'atomicmass' must be a positive number!")
            
            self.__del__()
            
        if isinstance(pseudopotential,str):
            self.pseudopotential=pseudopotential
        else:
            raise AtomTypeError("'pseudopotential' must be a string!")
            
            self.__del__()

        AtomType.__AtomTypes__.append(self)
        
    def __del__(self):
        '''
        __del__() -> class destructor.

        Returns
        -------
        None.
        '''
        pass
    
class Atom:
    __curratomid__=0     # ID available for a new atom
    
    def __init__(self,atomtype,x=[0.0,0.0,0.0],fixed=[False,False,False]):
        '''
        __init__(atomtype,x,fixed) -> class constructor.

        Parameters
        ----------
        atomtype : AtomType object
            Atomic species of the atom.
        x : Python list, optional
            Cartesian coordinates of the atom. The default is [0.0,0.0,0.0].
        fixed : Python list, optional
            Defines if an atom component should remain unaltered in the course
            of a geometry optimization. The default is [False,False,False].

        Returns
        -------
        None.
        '''
        if isinstance(atomtype,AtomType):
            self.symbol=atomtype.symbol
            self.element=atomtype.element
            self.atomicnumber=atomtype.atomicnumber
            self.atomicmass=atomtype.atomicmass
        else:
            raise AtomError("'atomtype' must be an AtomType object!")
            
            self.__del__()
            
        if isinstance(x,list) and len(x)==3:
            self.x=x
        else:
            raise AtomError("'x' must be a list with three components!")
            
            self.__del__()
            
        if isinstance(fixed,list) and len(fixed)==3:
            self.fixed=fixed
        else:
            raise AtomError("'fixed' must be a list with three components!")
            
            self.__del__()
            
        self.id=Atom.__curratomid__
        Atom.__curratomid__+=1
            
    def displace_atom(self,disp=[0.0,0.0,0.0]):
        '''
        displace_atom(disp) -> displaces the atom from its current position.

        Parameters
        ----------
        disp : Python list, optional
             Displacement vector. The default is [0.0,0.0,0.0].

        Returns
        -------
        None.
        '''
        
        if isinstance(disp,list) and len(disp)==3:
            self.x[0]+=disp[0]
            self.x[1]+=disp[1]
            self.x[2]+=disp[2]
            
    def move_atom_to(self,x=[0.0,0.0,0.0]):
        '''
        move_atom_to(x) -> moves the atom to a new position.

        Parameters
        ----------
        x : Python list, optional
            New atom position. The default is [0.0,0.0,0.0].

        Returns
        -------
        None.
        '''       
        if isinstance(x,list) and len(x)==3:
            self.x[0]=x[0]
            self.x[1]=x[1]
            self.x[2]=x[2]
            
    def duplicate_atom(self):
        '''
        duplicate_atom() -> returns a copy of the current Atom object.

        Returns
        -------
        Atom object
            Copy of the atom.
        '''
        newatom=deepcopy(self)
        newatom.id=Atom.__curratomid__
        Atom.__curratomid__+=1
        
        return newatom
            
    def __del__(self):
        '''
        __del__() -> class destructor.

        Returns
        -------
        None.
        '''
        pass
    
class AtomTypeError(BasicException):
    pass

class AtomError(BasicException):
    pass