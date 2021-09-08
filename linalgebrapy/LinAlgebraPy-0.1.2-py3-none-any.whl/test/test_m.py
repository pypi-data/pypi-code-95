from math import pi, sqrt
from time import perf_counter, process_time

import LinAlgebraPy
d=perf_counter()
from LinAlgebraPy import *
from LinAlgebraPy.matrices.matrixfunc import sortList

ve1=Vector(2,3,4,2).transpose().normalize()
ve2=Vector(3,4,2,4).transpose().normalize()
ve3=Vector(3,2,4,3).transpose().normalize()
mav=Matrix(ve1,ve2,ve2)
print(mav)


c=Matrix([2,1,3,2,5],[7,3,4,3,6],[8,7,4,1,2])
m1=Matrix([0,0,0],[0,9,1])
v1=Vector([2],[3],[3])
v2=Vector([3,2,3,3])
v3=Vector([2])
m2=Matrix([3e-3,2,3],[5,7,2],[4,9,1])
m3=Matrix([2,0],[0,0],[1,2])
np1=Matrix([5,2,4],[10,4,8],[2,6,12])
np2=Vector([0],[0],[0])
np1E=np1.echelon("RREF")
np2E=np1.echelonWithN(np2)
print(m2)
print(np1E)
print(np2E)
(m,n)=np1.dim
Vect=[np1E["L",i] for i in range(m)]
index=[indexPivot(x) for x in Vect]
matrixbig=Matrix([2,1,3,2,5,2,1,3,2,5,2,1,3,2,5,8,7,4,1,2],[2,1,3,2,5,2,1,3,2,5,2,1,3,2,5,8,7,4,1,2],[2,1,3,2,5,2,1,3,2,5,2,1,3,2,5,8,7,4,1,2])

print(matrixbig)
print(index)
print(m1.echelon(choice="RREF"))
print(v1.normalize(),v1*2,v1,v1.magn,v1.dim,v1.isColumn,v1.isNul(),v1.transpose(),sep="\n")
print(v2.normalize(),v2*2,v2,v2.magn,v2.dim,v2.isColumn,v2.isNul(),v2.transpose(),sep="\n")
m3.transpose(); m3.echelon() ; m3.echelonWithN(m3) ; m3.echelon(choice="REF") ; m3.echelon(choice="RREF")
m3.isSquared ; m3*m1; 
print(v3,v3.dim,v3.isLine)
print(m2.trace(),m2.det(),~m2,~m2*m2,sep="\n")

print(c.echelonWithN(v1))
f=perf_counter()
print(f-d)






