from LinAlgebraPy.vectors.vector import Vector
from math import sqrt

def onlytypeM(elements,types):
    res=0
    if types==list:
        for i in elements:
            if type(i)==list and len(i)==len(elements[0]): 
                res+=1 
        return len(elements)==res
    elif types==tuple:
        for i in elements:
            if type(i)==tuple and len(i)==len(elements[0]): 
                res+=1 
        return len(elements)==res
    elif types==Vector:  
        for i in elements:      
            if type(i)==Vector and i.dim == elements[0].dim and i.isLine:  
                res+=1
            elif type(i)==Vector and i.dim == elements[0].dim and i.isColumn:
                res+=sqrt(2)
        return res
    else:
        raise TypeError("Type allowed are Vector and List")
        
def imin(L, i):
    m = i
    for j in range(i + 1, len(L)): # i+1 … len(L)-1
        if L[j] < L[m]:
            m = j
    return m

def sortList(L,Vect):
    n = len(L)
    k,neg=0,1
    for i in range(n-1):
        m = imin(L,i) # minimum de la fin de liste
        if i==m and not Vect[i].isNul():
            continue
        (L[i], L[m]) = (L[m], L[i]) # échange
        (Vect[i], Vect[m]) = (Vect[m], Vect[i])
        neg*=-1
        if L[i]==-1:
            k+=1
    L=L[k:]+L[:k]
    Vect=Vect[k:]+Vect[:k]
    return (L,Vect,k,neg)

def sortMatrix(L,Vect,M):
    n = len(L)
    k,neg=0,1
    for i in range(n-1):
        m = imin(L,i) # minimum de la fin de liste
        if i==m:
            continue
        (L[i], L[m]) = (L[m], L[i]) # échange
        (Vect[i], Vect[m]) = (Vect[m], Vect[i])
        (M[i], M[m]) = (M[m], M[i])
        neg*=-1
        if L[i]==-1:
            k+=1
    L=L[k:]+L[:k]
    Vect=Vect[k:]+Vect[:k]
    M=M[k:]+M[:k]
    return (L,Vect,k,neg,M)