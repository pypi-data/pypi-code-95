from math import sqrt

def onlytype(elements,*types):
    nolen=[int,complex,float]
    for i in elements:
        if type(i) not in nolen:
            if type(i) not in types or len(i)!=1: 
                return False
        else:
            if type(i) not in types: 
                return False
    return True



def magnitude(elements):
    if onlytype(elements,list):
        res=0
        for i in elements:
            res+= abs(i[0]**2)
        return sqrt(res)
    else:
        res=0
        for i in elements:
            res+= abs(i**2)
        return sqrt(res)

class Vector():
    def __init__(self,*coord):
        length=len(coord)
        i=0
        types=[float,int,complex,list,tuple]
        elements=[]
        only=onlytype(coord,list)
        while i<length:
            c=coord[i]      
            if type(c) in types:
                if type(c) in types[0:3]:
                    elements.append(c)
                elif type(c)==list :
                    if only and len(c)!=1:
                        elements+=[[i] for i in c]
                    elif only and len(c)==1:
                        elements.append(c)
                    else:
                        elements+=c
                elif type(c)==tuple:
                    elements+=list(c)
            else:
                raise TypeError("Arguments allowed are float,int,complex,list,tuple ")
            i+=1
          
    
        self.elements=elements
        self.magn=magnitude(elements)
        self.isColumn=onlytype(elements,list)
        self.isLine=onlytype(elements,float,int,complex)

        if self.isColumn:
            self.dim=(len(self.elements),1)
            for  i in range(self.dim[0]):
                elem=elements[i][0]
                instance=type(elem)          
                if instance!=complex and elem<=1e-14 and elem>=-1e-14:  #changed type in echelon with N and Echelon
                    elements[i][0]=0
                elif instance==complex:
                    real=complex(elements[i][0]).real
                    imag=complex(elements[i][0]).imag
                    comparereal=(real<=1e-13 and real>=-1e-13) 
                    compareimag=(imag<=1e-13 and imag>=-1e-13)
                    if comparereal and compareimag:
                        elements[i][0]=0;
                    elif compareimag:
                        elements[i][0]=round(real,13)
                    elif comparereal:
                        elements[i][0]=round(imag,13)*1j
        else:
            self.dim=(1,len(self.elements)) 
            for  i in range(self.dim[1]):
                elem=elements[i]
                instance=type(elem)          
                if instance!=complex and elem<=1e-13 and elem>=-1e-13:  #changed type in echelon with N and Echelon
                    elements[i]=0
                elif instance==complex:
                    real=complex(elements[i]).real
                    imag=complex(elements[i]).imag
                    comparereal=(real<=1e-13 and real>=-1e-13) 
                    compareimag=(imag<=1e-13 and imag>=-1e-13)
                    if comparereal and compareimag:
                        elements[i]=0;
                    elif compareimag:
                        elements[i]=round(real,14)
                    elif comparereal:
                        elements[i]=round(imag,14)*1j
             
        
    def __repr__(self) :
        if self.isLine:
            return str(tuple(self.elements))
        else:
            string=''
            for i in self.elements:
                string+='( {} ) \n'.format(i[0])
            return string
    def __getitem__(self,i):
        if self.isLine:
            return self.elements[i]
        else:
            return self.elements[i][0]
    def __setitem__(self,i,val):
        elem=self.elements
        instance=type(val)          
        if instance!=complex and val<=1e-14 and val>=-1e-14:  #changed type in echelon with N and Echelon
            val=0
        elif instance==complex:
            real=complex(val).real
            imag=complex(val).imag
            comparereal=(real<=1e-13 and real>=-1e-13) 
            compareimag=(imag<=1e-13 and imag>=-1e-13)
            if comparereal and compareimag:
                val=0;
            elif compareimag:
                val=round(real,14)
            elif comparereal:
                val=round(imag,14)*1j
                
        if self.isLine:
            if len(elem)==0:
                elem.append(val)
            elif i<len(elem) and i>=0:
                elem[i]=val
            else:
                raise IndexError("Index out of range")
        else:
            if len(elem)==0:
                elem.append([val])
            elif i<len(elem) and i>=0:
                elem[i]=[val]
            else:
                raise IndexError("Index out of range")  
    def __add__(self,var):
        types=[list,tuple,Vector]
        if type(var) in types:
            if type(var)==Vector:
                if self.dim!=var.dim:
                    raise ValueError("Vectors cannot add with different number of dimensions.")
                else:
                    length=len(self.elements)
                    v1,v2=self.elements,var.elements
                    if self.isLine:
                        elements= [v1[i]+ v2[i] for i in range (length)]
                    else:
                        elements= [[v1[i][0]+ v2[i][0]] for i in range (length)]
                    vect=Vector(elements)
                    return vect
            elif type(var)==list :
                if self.isLine:
                    elem=self.elements + var
                else:
                    elem=self.elements + [var]
                vect=Vector(elem)
                return vect
            else:
                if self.isLine:
                    elem=self.elements + list(var)
                else:
                    elem=self.elements + [list(var)]
                vect=Vector(elem)  
                return vect
        else:
            raise TypeError("Arguments allowed for adding are list and tuple ")
    def __radd__(self,var):
        return self.__add__(var)
    def __IADD__(self,var):
        return self.__add__(var)
    def __sub__(self,var):
        if type(var)==Vector:
            (m1,n1)=self.dim
            length=len(self.elements)
            v1,v2=self.elements,var.elements
            if self.isLine and var.isLine:
                elements= [v1[i]-v2[i] for i in range (length)]
                vect=Vector(elements)
            elif self.isColumn and var.isColumn :
                if m1==1:
                    elements= [v1[0][0]-v2[0][0]]
                else:
                    elements= [[v1[i][0]-v2[i][0]] for i in range (length)]
                vect=Vector(elements)  
            else:
                raise ValueError("For substraction, the values shoul be two vectors and the same dimension")
            return vect
        else:
            raise TypeError("Substraction should be with another Vector")
    def __ISUB__(self,var):
        return self.__sub__(var)
    def __rsubb__(self,var):
        return self.__sub__(var)
    def __mul__(self,var):
        (m1,n1)=self.dim
        if type(var)==Vector:
            (m2,n2)=var.dim
            res=0
            if n1==m2 and self.isLine:     
                for i in range(n1):
                    res+=self.elements[i]*var.elements[i][0]
                return Vector(res)
            else:           
                raise ValueError("Multiplying two vectors cannot be done if i of the first vector is not equal to j of the second vector or the Product returns a matrix")
        else:
            v1=self.elements
            length=len(self.elements)
            if self.isLine:
                vect= Vector([v1[i]*var for i in range(length)])
            else:
                if m1==1:
                    vect= Vector([v1[0][0]*var])
                else:
                    vect= Vector([[v1[i][0]*var] for i in range(length)])
            return vect
    def __rmul__(self,var):
        return self.__mul__(var)
    def __eq__(self, other) :
        if self.isLine and other.isLine:
            first=self.elements
            second=other.elements
            for i in range(len(first)):
                if first[i]!=second[i]:
                    return False
            return True
        elif self.isColumn and other.isColumn:
            first=self.elements
            second=other.elements
            for i in range(len(first)):
                if first[i][0]!=second[i][0]:
                    return False
            return True
        else:
            raise ValueError("The dimensions of the two vectors are not equal for comparing")

    def normalize(self):
        magnitude=self.magn
        if magnitude==0:
            raise ZeroDivisionError("Cannot normalize a zero-vector")
        else:
            vect=Vector(self.elements)
            return vect*(1/magnitude)
    def transpose(self):
        elem=self.elements
        if self.isLine:
            vect=Vector([[i] for i in elem])
        else:
            vect=Vector([i[0] for i in elem])
        return vect

    def isNul(self):
        if self.isLine:
            for  i in self.elements:
                if i!=0:
                    return False
        else:
            for  i in self.elements:
                if i[0]!=0:
                    return False
        return True
        
def scalarproduct(vect1,vect2):
    if type(vect1)==Vector and  type(vect2)==Vector:
        (m1,n1)=vect1.dim
        (m2,n2)=vect2.dim
        res=0
        if m1==m2 and vect1.isColumn and vect2.isColumn:     
            for i in range(m1):
                res+=vect1.transpose().elements[i]*vect2.elements[i][0]
            return res
        elif n1==n2 and vect1.isLine and vect2.isLine:
            for i in range(n1):
                res+=vect1.transpose().elements[i][0]*vect2.elements[i]
            return res
        else:
            raise ValueError("The vectors should be the same Dimension")
    else:
        raise ValueError("Only vectors allowed for scalar product")

def orthogonalVectors(vectors):
    length=len(vectors)
    for i in range(length):
        if type(vectors[i])==Vector:
            for j in range(i+1,length):
                if scalarproduct(vectors[i],vectors[j])!=0:
                    return False
        else:
            raise TypeError("Arguments should be only vectors with same dimension")
    return True 

def indexPivot(vector):
    i=vector.elements
    for j in range(len(i)):
        if i[j]!=0:
            return  j
    return -1

def indexPivotColumn(vector):
    i=vector.elements
    for j in range(len(i)):
        if i[j][0]!=0:
            return j
    return -1
def colinear(vect1,vect2):  #Still Imcomplete
    no,res,g=0,0,0
    (n,m)=vect1.dim
    vec1=vect1.elements
    vec2=vect2.elements
    i=0
    while i<m:
        if (vec1[i]!=0) ^ (vec2[i]!=0):
            return False
        if vec2[i]!=0 and vec1[i]!=0:
            if vec1[i]%vec2[i]==0:
                res= vec1[i]/vec2[i]
                g=1
                break
            elif vec2[i]%vec1[i]==0:
                res= vec2[i]/vec1[i]
                g=2
                break
        i+=1
    if g==1:
        return vect1==res*vect2
    elif g==2:
        return vect2==res*vect1

    elif vect1.isNul and vect2.isNul:
        return True


