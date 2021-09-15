pi = 3.141592653589793
def factorial(n):
	fact = 1
	for i in range(1,n+1):
		fact = fact * i
	return fact
def sin(x, d):
    p = 0
    for n in range(d):
        p += ((-1)**n)*(x**(2*n+1))/(factorial(2*n+1))
    return p
def sqrt(x, i):
	n = 1
	for _ in range(i):
		n = (n + x/n) * 0.5
	return n
def grlpi(amt,prec,o=False):
  #Gregory-Leibniz
  c=1
  p=0
  for i in range(amt):
    if(i%2==1):  
      p-=4/c  
    else:
      p+=4/c
    c+=2
    if(i%1000==0 and o):
      print(("iter"+str(i)+" {0:."+str(prec)+"f}").format(p))
  return p

def nkpi(a,p,o=False):
  #Nilakantha
  s=3
  d=2
  si=1
  i=1
  for k in range(a):
    s+=si*(4 / (d*(d+1)*(d+2)))
    if(k%1000==0 and o):
      print(("iter"+str(k)+" {0:."+str(p)+"f}").format(s))
    d+=2
    if si == 1:
      si=-1
    else:
      si=1
  return s
def ampi(n,p,o=False):
  #Archimedes
  #thanks to https://stackoverflow.com/questions/46594908/archimedes-pi-approximation-in-python for this code <3
  sides = 4
  if(n>511):
    raise ValueError("""No value greater than 511 permitted. 
    This would crash your system, and Python doesn't allow such a thing.""")
    return
  for i in range(n):
    value = math.pi/180*(360/(2*sides))
    sinvalue = sin(value, n/4)
    PI = sinvalue * sides
    sides *=4
    if(i%10==0 and o):
      print(("iter"+str(i)+" {0:."+str(p)+"f}").format(PI))
  return PI
      
def galpi(n,p,o=False):
  a = 1
  b = 1/sqrt(2, int(n/4))
  t = 1/4
  x = 1
  for k in range(n):
    y = a
    a = (a+b)/2
    b = sqrt(b*y, int(n/4))
    t = t - x * ((y-a))**2
    x = 2* x
    pi = (((a+b))**2)/(4*t)
    if(k%100==0 and o):
      print(("iter"+str(k)+" {0:."+str(p)+"f}").format(pi))
  return pi

def cpi(n,p,o=False):
	pi = 0
	for k in range(1,n-1):
		pi += sqrt(1-((k/n)**2), int(n/4))
		if(k%100==0 and o):
			print(("iter"+str(k)+" {0:."+str(p)+"f}").format(4*(pi/n)))
	return (4*(pi/n))