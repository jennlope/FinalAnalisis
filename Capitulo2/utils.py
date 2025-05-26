import numpy as np

def jacobi(A, b, x0, tol, niter):
    n = len(A)
    x = x0.copy()
    iteraciones = []

    for i in range(len(A)):
        if A[i][i] == 0:
            raise ValueError(f"Jacobi no puede ejecutarse: A[{i}][{i}] = 0 provoca división por cero.")

    for k in range(niter):
        x_new = x.copy()
        for i in range(n):
            suma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - suma) / A[i][i]
        error = np.linalg.norm(np.array(x_new) - np.array(x))

        iteraciones.append([k+1, *x_new, error])
        if error < tol:
            break
        x = x_new
    return iteraciones


def gauss_seidel(A, b, x0, tol, niter):
    n = len(A)
    x = x0.copy()
    iteraciones = []
    
    for i in range(len(A)):
        if A[i][i] == 0:
            raise ValueError(f"Gauss-seidel no puede ejecutarse: A[{i}][{i}] = 0 provoca división por cero.")


    for k in range(niter):
        x_new = x.copy()
        for i in range(n):
            suma1 = sum(A[i][j] * x_new[j] for j in range(i))
            suma2 = sum(A[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = (b[i] - suma1 - suma2) / A[i][i]
        error = np.linalg.norm(np.array(x_new) - np.array(x))
        iteraciones.append([k+1, *x_new, error])
        if error < tol:
            break
        x = x_new
    return iteraciones


def sor(A, b, x0, tol, niter, w):
    n = len(A)
    x = x0.copy()
    iteraciones = []
    
    for i in range(len(A)):
        if A[i][i] == 0:
            raise ValueError(f"SOR no puede ejecutarse: A[{i}][{i}] = 0 provoca división por cero.")


    for k in range(niter):
        x_new = x.copy()
        for i in range(n):
            suma1 = sum(A[i][j] * x_new[j] for j in range(i))
            suma2 = sum(A[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = (1 - w) * x[i] + (w / A[i][i]) * (b[i] - suma1 - suma2)
        error = np.linalg.norm(np.array(x_new) - np.array(x))

        iteraciones.append([k+1, *x_new, error])
        if error < tol:
            break
        x = x_new
    return iteraciones
