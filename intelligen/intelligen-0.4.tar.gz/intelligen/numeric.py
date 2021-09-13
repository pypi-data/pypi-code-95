import numpy as np

def newton(f, df, x, tol, iter = False) -> float:
    ''' Newton Method '''
    n = 0
    while abs(f(x))>tol:
        x = x - f(x) / df(x)
        n += 1
    if iter: return x, n
    return x


def bisection(f, xi, xf, tol, iter = False, n=1) -> float:
  if f(xi) * f(xf) < 0:
    xm = (xi + xf) / 2
    
    if abs(f(xm)) < tol:
      if iter: return xm, n
      return xm

    if f(xi) * f(xm) < 0:
      return bisection(f, xi, xm, tol, iter, n+1)
    
    if f(xm) * f(xf) < 0:
      return bisection(f, xm, xf, tol, iter, n+1)

  else:
    print("Invalid input")


def regula_falsi(f, xi, xf, tol, iter = False, n=1) -> float:
  if f(xi) * f(xf) < 0:
    xm = (xi * f(xf) - xf * f(xi)) / (f(xf) - f(xi))
    
    if abs(f(xm)) < tol:
      if iter: return xm, n
      return xm

    if f(xi) * f(xm) < 0:
      return regula_falsi(f, xi, xm, tol, iter, n+1)
    
    if f(xm) * f(xf) < 0:
      return regula_falsi(f, xm, xf, tol, iter, n+1)

  else:
    print("Invalid input")


def secant(f, x0, x1, tol, iter = False, n=1) -> float:
  x2 = x1 - (f(x1) * (x1 - x0)) / (f(x1) - f(x0))
  
  if abs(f(x2)) < tol:
    if iter: return x2, n
    return x2

  else:
    return secant(f, x1, x2, tol, iter, n+1)


""" def fixed_point(g, dg, x, tol, iter = False):
  ''' f(x) = 0 ==> x = g(x) '''
  n = 1
  if abs(dg(x))<1:
    xa = x
    x = g(x)
    
    while abs(x-xa)>tol:
      xa = x
      x = g(x)
      n = n+1

    if iter: return x, n
    return x

  else:
    print("Doesn't converge")  """


def newton2(f, df, ddf, x, tol, iter = False, n=0) -> float:
  if abs(f(x)) < tol:
    if iter: return x, n
    return x
  
  else:
    x1 = x - df(x) / ddf(x) + np.sqrt(df(x)**2 - 2*ddf(x) * f(x)) / ddf(x)
    x2 = x - df(x) / ddf(x) - np.sqrt(df(x)**2 - 2*ddf(x) * f(x)) / ddf(x)

    if abs(f(x1)) < abs(f(x2)):
      return newton2(f, df, ddf, x1, tol, iter, n+1)
    else:
      return newton2(f, df, ddf, x2, tol, iter, n+1)


def main() -> None:
    f   = lambda x: x**3 + 2*x**2 + 10*x - 20
    df  = lambda x: 3*x**2 + 4*x + 10
    ddf = lambda x: 6*x + 4

    g   = lambda x: (-x**3 - 2*x**2 + 20) / 10
    dg  = lambda x: (-3*x**2 - 4*x) / 10

    print(newton(f, df, 1, 0.01, True))
    print(bisection(f, 1, 2, 0.01, True))
    print(regula_falsi(f, 1, 2, 0.01, True))
    #print(fixed_point(g, dg, 0, 0.1, True))
    print(newton2(f, df, ddf, 1, 0.01, True))

if __name__ == '__main__':
    main()