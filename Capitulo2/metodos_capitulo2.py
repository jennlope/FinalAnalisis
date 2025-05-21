# Capitulo2/metodos_capitulo2.py

import numpy as np
import time
from numpy.linalg import norm, eigvals


def calcular_radio_espectral(matriz_transicion):
    valores_propios = eigvals(matriz_transicion)
    return max(abs(valores_propios))


def jacobi(A, b, tol=1e-6, max_iter=100):
    n = len(A)
    x = np.zeros(n)
    iteraciones = []
    D = np.diag(A)
    R = A - np.diagflat(D)
    M = np.diagflat(1 / D) @ R
    radio = calcular_radio_espectral(M)

    inicio = time.time()
    for _ in range(max_iter):
        x_new = (b - np.dot(R, x)) / D
        iteraciones.append(x_new.copy())
        if norm(x_new - x, ord=np.inf) < tol:
            break
        x = x_new
    fin = time.time()

    converge = radio < 1
    return {
        "nombre": "Método de Jacobi",
        "iteraciones": iteraciones,
        "radio": radio,
        "estado": "✅ Converge" if converge else "❌ No Converge",
        "tiempo": round(fin - inicio, 6),
        "clase": "jacobi"
    }


def gauss_seidel(A, b, tol=1e-6, max_iter=100):
    n = len(A)
    x = np.zeros(n)
    iteraciones = []
    L = np.tril(A)
    U = A - L
    M = -np.linalg.inv(L) @ U
    radio = calcular_radio_espectral(M)

    inicio = time.time()
    for _ in range(max_iter):
        x_new = np.copy(x)
        for i in range(n):
            suma1 = np.dot(A[i, :i], x_new[:i])
            suma2 = np.dot(A[i, i+1:], x[i+1:])
            x_new[i] = (b[i] - suma1 - suma2) / A[i, i]
        iteraciones.append(x_new.copy())
        if norm(x_new - x, ord=np.inf) < tol:
            break
        x = x_new
    fin = time.time()

    converge = radio < 1
    return {
        "nombre": "Método de Gauss-Seidel",
        "iteraciones": iteraciones,
        "radio": radio,
        "estado": "✅ Converge" if converge else "❌ No Converge",
        "tiempo": round(fin - inicio, 6),
        "clase": "gs"
    }


def sor(A, b, w=1.25, tol=1e-6, max_iter=100):
    n = len(A)
    x = np.zeros(n)
    iteraciones = []
    D = np.diagflat(np.diag(A))
    L = -np.tril(A, -1)
    U = -np.triu(A, 1)
    M = np.linalg.inv(D - w * L) @ ((1 - w) * D + w * U)
    radio = calcular_radio_espectral(M)

    inicio = time.time()
    for _ in range(max_iter):
        x_new = np.copy(x)
        for i in range(n):
            sigma = np.dot(A[i, :i], x_new[:i]) + np.dot(A[i, i + 1:], x[i + 1:])
            x_new[i] = (1 - w) * x[i] + (w / A[i, i]) * (b[i] - sigma)
        iteraciones.append(x_new.copy())
        if norm(x_new - x, ord=np.inf) < tol:
            break
        x = x_new
    fin = time.time()

    converge = radio < 1
    return {
        "nombre": "Método SOR (w = {:.2f})".format(w),
        "iteraciones": iteraciones,
        "radio": radio,
        "estado": "✅ Converge" if converge else "❌ No Converge",
        "tiempo": round(fin - inicio, 6),
        "clase": "sor"
    }
