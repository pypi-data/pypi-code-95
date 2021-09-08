from math import  sqrt


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


