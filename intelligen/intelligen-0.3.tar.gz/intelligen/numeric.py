import numpy as np

def newton(f, df, x, tol, iter = False):
    ''' Newton Method '''
    n = 0
    while abs(f(x))>tol:
        x = x - f(x) / df(x)
        n += 1
    if iter: return x, n
    return x


def bisection(f, xi, xf, tol, n=1, iter = False):
  if f(xi) * f(xf) < 0:
    xm = (xi + xf) / 2
    
    if abs(f(xm)) < tol:
      if iter: return xm, n
      return xm

    if f(xi) * f(xm) < 0:
      return bisection(f, xi, xm, tol, n+1, iter)
    
    if f(xm) * f(xf) < 0:
      return bisection(f, xm, xf, tol, n+1, iter)

  else:
    print('Invalid input')


def regula_falsi(f, xi, xf, tol, n=1, iter = False):
  if f(xi) * f(xf) < 0:
    xm = (xi * f(xf) - xf * f(xi)) / (f(xf) - f(xi))
    
    if abs(f(xm)) < tol:
      if iter: return xm, n
      return xm

    if f(xi) * f(xm) < 0:
      return regula_falsi(f, xi, xm, tol, n+1, iter)
    
    if f(xm) * f(xf) < 0:
      return regula_falsi(f, xm, xf, tol, n+1, iter)

  else:
    print('Invalid input')


def secant(f, x0, x1, tol, n=1, iter = False):
  x2 = x1 - (f(x1) * (x1 - x0)) / (f(x1) - f(x0))
  
  if abs(f(x2)) < tol:
    if iter: return x2, n
    return x2

  else:
    return secant(f, x1, x2, tol, n+1, iter)


""" def fixed_point(f, df, x, tol, n=1, iter = False):
  if abs(df(x))<1:
    xa = x
    x = f(x)
    while abs(x-xa)>tol:
      xa = x
      x = f(x)
      n = n+1
    return x,n

  else:
    print("No converge")  """



""" f = lambda x: x**3 + 2*x**2 + 10*x-20
df = lambda x: 3*x**2 + 4*x + 10
ddf = lambda x: 6*x + 4

print(newton(f, df, 1, 0.01, True))
print(bisection(f, 1, 2, 0.01, iter=True))
print(regula_falsi(f, 1, 2, 0.01, iter=True)) """