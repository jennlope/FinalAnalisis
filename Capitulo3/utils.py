import numpy as np
import math
import sympy as sp

def vandermonde(x, y):
    n = len(x)
    A = np.vander(x, increasing=False)
    a = np.linalg.solve(A, y)
    x_sym = sp.Symbol('x')
    poly = sum(a[i] * x_sym**(n - 1 - i) for i in range(n))
    return poly.simplify(), a

def lagrange(x, y):
    n = len(x)
    x_sym = sp.Symbol('x')
    pol = 0
    for i in range(n):
        term = y[i]
        for j in range(n):
            if j != i:
                term *= (x_sym - x[j]) / (x[i] - x[j])
        pol += term
    return sp.simplify(pol)

def newton_divididas(x, y):
    n = len(x)
    coef = list(y)
    for j in range(1, n):
        for i in range(n-1, j-1, -1):
            coef[i] = (coef[i] - coef[i-1]) / (x[i] - x[i-j])

    x_sym = sp.Symbol('x')
    pol = coef[0]
    for i in range(1, n):
        term = coef[i]
        for j in range(i):
            term *= (x_sym - x[j])
        pol += term
    return sp.simplify(pol), coef

def spline_lineal(x, y):
    x_sym = sp.Symbol('x')
    n = len(x)
    splines = []
    for i in range(n - 1):
        m = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        b = y[i] - m * x[i]
        s = m * x_sym + b
        intervalo = (x[i], x[i + 1])
        splines.append((sp.simplify(s), intervalo))
    return splines

def spline_cubico(x, y):
    from scipy.interpolate import CubicSpline
    x_sym = sp.Symbol('x')
    cs = CubicSpline(x, y, bc_type='natural')
    splines = []
    for i in range(len(x) - 1):
        c = cs.c[:, i]
        s = c[0]*(x_sym - x[i])**3 + c[1]*(x_sym - x[i])**2 + c[2]*(x_sym - x[i]) + c[3]
        intervalo = (x[i], x[i+1])
        splines.append((sp.simplify(s), intervalo))
    return splines
