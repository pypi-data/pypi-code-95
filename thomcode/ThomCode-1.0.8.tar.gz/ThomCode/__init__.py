import math, random, numpy as np, string

def getInteger( prompt ):
    while True:
        try:
            num = int( input( prompt ) )
        except ValueError:
            print( "sorry, you are only allowed to use integers (whole numbers). please try again..." )
            continue
        return num

def getFloat( prompt ):
    while True:
        try:
            num = float( input( prompt ) )
        except ValueError:
            print( "sorry, you are only allowed to use numbers. please try again..." )
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
            print( "sorry, u mag enkel 1 character gebruiken. please try again..." )
            continue
        if line < 'A' or line > 'Z':
            print( "sorry, you are only allowed to use a single letter from the alphabet. please try again..." )
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
            print("sorry, with BinomialCoef function the 'n' must be equal or bigger then 'k'.\n")
            return

def pi():
    return (math.pi)

def factorial(num):
    return math.factorial(num)

def CircleCir(radius):
    return  (radius*2*pi)

def CircleSurf(radius):
    return (pi*(radius**2))

def SphereVol(radius):
    return ((pi * (radius*2)**3)/6)
    
def TriangleSurf (base,height):
    return (0,5 * base * height)

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

def reversed(data):
    if type(data) is list:
        data.reverse() # PAS OP DIT KLOPT!!!
        return data
    elif type(data) is int:
        return (int(str(data)[::-1]))
    return (data[::-1])

def FibonacciList(max):
    list =[]
    for i in range(max):
        if Fibonacci_CALC(i) > max:
            break
        list.append (Fibonacci_CALC(i))
    return list

def Fibonacci_CALC(n):
    
   if n <= 1:
       return n
   else:
       return(Fibonacci_CALC(n-1) + Fibonacci_CALC(n-2))

def FibonacciNum(integer):
    if integer<= 0:
        return
    elif integer == 1:
        return 0
    elif integer == 2:
        return 1
    else:
        return FibonacciNum(integer-1)+FibonacciNum(integer-2)

def radians(degrees):
    degrees = degrees/180*pi
    return degrees

def degrees(radians):
    radians = radians/pi*180
    return radians

def AlphabetList():
    x = string.ascii_lowercase
    y = list(x)
    return (y)

def AlphabetListCAP():
    x = string.ascii_uppercase
    y = list(x)
    return (y)

def NumberList(max):
    list = []
    for i in range(max):
        list.append(i+1)
    return list

def RandomMatrix(X_spread, Y_spread, min, max):

    list = [[random.randint(min,max) for i in range(Y_spread)] for j in range(X_spread)]
    return np.array(list)

def MatrixMultiplier (matrix1, matrix2):
    arr1 = matrix1
    arr2 = matrix2
    if len(arr1[0]) == len(arr2):
        arr3 = RandomMatrix(len(arr1),len(arr2[0]),0,0)
    else:
        print ("\n>>> multiply not possible with these matrices.")
        return 

    for i in range( len(arr1) ):
       for j in range(len(arr2[0])):
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

def MatrixSub(matrix1, matrix2):
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
AlphabetListCAP = AlphabetListCAP()
