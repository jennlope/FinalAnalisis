import numpy as np
from django.core.cache import cache

def is_diagonally_dominant(A):
    """Verifica si la matriz es diagonalmente dominante"""
    D = np.diag(np.abs(A))
    S = np.sum(np.abs(A), axis=1) - D
    return np.all(D > S)

def spectral_radius(T):
    """Calcula el radio espectral de una matriz"""
    return np.max(np.abs(np.linalg.eigvals(T)))

def jacobi(A, b, x0, tol, max_iter):
    """
    Método de Jacobi para sistemas lineales Ax = b
    Args:
        A: Matriz de coeficientes
        b: Vector de términos independientes
        x0: Vector inicial
        tol: Tolerancia
        max_iter: Máximo de iteraciones
    Returns:
        Diccionario con resultados, radio espectral y convergencia
    """
    D = np.diag(np.diag(A))
    LU = A - D
    T = -np.linalg.inv(D) @ LU
    rho = spectral_radius(T)
    
    resultados = []
    x = x0.copy()
    
    for k in range(max_iter):
        x_new = np.linalg.inv(D) @ (b - LU @ x)
        error = np.linalg.norm(x_new - x, np.inf)
        
        resultados.append({
            'iter': k + 1,
            'x': np.round(x_new, 6).tolist(),
            'error': np.round(error, 6)
        })
        
        if error < tol:
            break
            
        x = x_new
    
    return {
        'resultados': resultados,
        'radio_espectral': np.round(rho, 6),
        'converge': rho < 1,
        'solucion': np.round(x, 6).tolist()
    }

def gauss_seidel(A, b, x0, tol, max_iter):
    """
    Método de Gauss-Seidel para sistemas lineales
    """
    L = np.tril(A)
    U = A - L
    T = -np.linalg.inv(L) @ U
    rho = spectral_radius(T)
    
    resultados = []
    x = x0.copy()
    
    for k in range(max_iter):
        x_new = np.linalg.inv(L) @ (b - U @ x)
        error = np.linalg.norm(x_new - x, np.inf)
        
        resultados.append({
            'iter': k + 1,
            'x': np.round(x_new, 6).tolist(),
            'error': np.round(error, 6)
        })
        
        if error < tol:
            break
            
        x = x_new
    
    return {
        'resultados': resultados,
        'radio_espectral': np.round(rho, 6),
        'converge': rho < 1,
        'solucion': np.round(x, 6).tolist()
    }

def sor(A, b, x0, omega, tol, max_iter):
    """
    Método SOR (Succesive Over-Relaxation)
    Args:
        omega: Parámetro de relajación (0 < omega < 2)
    """
    if omega <= 0 or omega >= 2:
        raise ValueError("Omega debe estar entre 0 y 2")
    
    D = np.diag(np.diag(A))
    L = np.tril(A, -1)
    U = np.triu(A, 1)
    
    T = np.linalg.inv(D + omega * L) @ ((1 - omega) * D - omega * U)
    rho = spectral_radius(T)
    
    resultados = []
    x = x0.copy()
    
    for k in range(max_iter):
        x_new = np.linalg.inv(D + omega * L) @ (omega * b - (omega * U + (omega - 1) * D) @ x)
        error = np.linalg.norm(x_new - x, np.inf)
        
        resultados.append({
            'iter': k + 1,
            'x': np.round(x_new, 6).tolist(),
            'error': np.round(error, 6),
            'omega': np.round(omega, 4)
        })
        
        if error < tol:
            break
            
        x = x_new
    
    return {
        'resultados': resultados,
        'radio_espectral': np.round(rho, 6),
        'converge': rho < 1,
        'solucion': np.round(x, 6).tolist(),
        'omega': omega
    }

def comparar_metodos(A, b, x0, omega, tol, max_iter):
    """
    Ejecuta los tres métodos y genera comparativa
    Returns:
        Diccionario con resultados de todos los métodos
        y el mejor método identificado
    """
    # Verificar diagonal dominante primero
    if not is_diagonally_dominant(A):
        cache.set('last_warning', 'La matriz no es diagonalmente dominante', 30)
    
    # Ejecutar métodos
    resultados = {
        'jacobi': jacobi(A, b, x0, tol, max_iter),
        'gauss_seidel': gauss_seidel(A, b, x0, tol, max_iter),
        'sor': sor(A, b, x0, omega, tol, max_iter)
    }
    
    # Identificar el mejor método (menos iteraciones)
    mejor_metodo = min(
        resultados.items(),
        key=lambda item: len(item[1]['resultados'])
    )
    
    return {
        'resultados': resultados,
        'mejor_metodo': mejor_metodo[0],
        'mejor_solucion': mejor_metodo[1]['solucion']
    }

def generar_matriz_ejemplo(n=3):
    """
    Genera una matriz de ejemplo diagonalmente dominante
    y su vector b asociado para propósitos de prueba
    """
    A = np.random.rand(n, n) * 10
    for i in range(n):
        A[i, i] = np.sum(np.abs(A[i])) + 1  # Hacerla diagonal dominante
    
    b = np.random.rand(n) * 10
    return A.round(2), b.round(2)