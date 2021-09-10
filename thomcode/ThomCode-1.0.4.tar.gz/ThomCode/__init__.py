import math, random, numpy as np

def getInteger( prompt ):
    while True:
        try:
            num = int( input( prompt ) )
        except ValueError:
            print( "sorry, er mogen alleen volledige getallen gebruikt worden. probeer het nogmaals" )
            continue
        return num

def getFloat( prompt ):
    while True:
        try:
            num = float( input( prompt ) )
        except ValueError:
            print( "sorry, er mogen alleen getallen gebruikt worden. probeer het nogmaals." )
            continue
        return num

def getString( prompt ):
    line = input( prompt )
    return line.strip()

def getLetter( prompt ):
    while True:
        line = input( prompt )
        line = line.strip()
        line = line.upper()
        if len( line ) != 1:
            print( "sorry, u mag enkel 1 character gebruiken. probeer het nogmaals." )
            continue
        if line < 'A' or line > 'Z':
            print( "sorrt, u mag alleen letters gebruiken uit het alfabet. probeer het nogmaals." )
            continue
        return line

def phythagoras(a,b):
    C = math.sqrt(a*a + b*b)
    return C

def sqrt(num):
    return math.sqrt(num)

def Sort_list(list):
    x = 1
    while True:
        rouleer = False
        for i in range(len(list)-x):
            if list[i] > list[i+1]:
                list[i], list[i+1] = list[i+1], list[i]
                rouleer = True
        x += 1

        if rouleer == False:
            return list

def BinomialCoef (n,k):
    while True:
        if n >= k:
            return (int(factorial(n)/(factorial(k)*factorial(n-k))) )    
        else:
            print("sorry, bij de BinomialCoef functie moet 'n' gelijk of groter zijn dan 'k'.\n")
            return

def pi():
    return (math.pi)

def factorial(num):
    return math.factorial(num)

def CircleCir(radius):
    radius = radius*2*pi
    return radius

def CircleSurf(radius):
    radius = pi*(radius**2)
    return radius

def SphereVol(radius):
    radius = (pi * (radius*2)**3)/6
    return radius

def PrimeChecker(num):
    if num == 0 or num == 1:
        return False
    for x in range(2, num):
        if num % x == 0:
            return False
    else:
        return True

def PrimeList(Max):
    antwoord = list()
    sieve = [True] * (Max+1)
    for p in range(2, Max+1):
        if (sieve[p]):
            antwoord.append(p)
            for i in range(p, Max+1, p):
                sieve[i] = False
    return antwoord

def ReverseList(list):
    list.reverse()
    return list

def FibonacciList(max):
    list =[]
    n = max
    for i in range(n):
        if Fibonacci_CALC(i) > n:
            break
        list.append (Fibonacci_CALC(i))
    return list

def Fibonacci_CALC(n): # hoort bij def fibonacci
    
   if n <= 1:
       return n
   else:
       return(Fibonacci_CALC(n-1) + Fibonacci_CALC(n-2))

def radians(degrees):
    degrees = degrees/180*pi
    return degrees

def degrees(radians):
    radians = radians/pi*180
    return radians

def AlphabetList():
    return ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

def NumberList(max):
    list = []
    x = 1
    for i in range(max):
        list.append(x)
        x +=1
    return list

def RandomMatrix(X_spread, Y_spread, min, max):

    list = [[random.randint(min,max) for i in range(Y_spread)] for j in range(X_spread)]
    return np.array(list)

def MatrixMultiplier (matrix1, matrix2):
    # matrix 1
    arr1 = matrix1
    # matrix 2
    arr2 = matrix2
    # result matrix
    if len(arr1[0]) == len(arr2):
        arr3 = RandomMatrix(len(arr1),len(arr2[0]),0,0)
        print (np.array(arr3))
    else:
        print ("\n>>> multiply not possible with these matrices.")
        return 

    # interatie van de rij van de X matrix
    for i in range( len(arr1) ):
       # interatie van de kolom van de Y matrix
       for j in range(len(arr2[0])):
           # interatie van de rij van de Y matrix
           for k in range(len(arr2)):
               arr3[i][j] += arr1[i][k] * arr2[k][j]
    return np.array(arr3)
    
def MatrixSum(matrix1, matrix2):
    if len(matrix1[0]) == len(matrix2[0]):
        if len(matrix1) == len(matrix2):
            arr3 = np.array(matrix1) + np.array(matrix2)
            return arr3
        else:
            print ("\n>>> sum not possible with these matrices.")
            return 
    else:
        print ("\n>>> sum not possible with these matrices.")
        return 

def MatrixMinus(matrix1, matrix2):
    if len(matrix1[0]) == len(matrix2[0]):
        if len(matrix1) == len(matrix2):
            arr3 = np.array(matrix1) - np.array(matrix2)
            return arr3
        else:
            print ("\n>>> minus not possible with these matrices.")
            return 
    else:
        print ("\n>>> minus not possible with these matrices.")
        return 
         


pi = pi()
AlphabetList = AlphabetList()
