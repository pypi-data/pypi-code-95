from const import *
from tools import *

x, y = read__sheet("""
Al 3
H 3
C 12
B 3
GaAs 7
O 12
GaInSb 12
N 1
""")

print(x, y)
print(is__consisted__of__chemical__elements('GaAsH'))