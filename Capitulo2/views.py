# Capitulo2/views.py
from django.shortcuts import render, redirect
import numpy as np
from .metodos_capitulo2 import jacobi, gauss_seidel, sor
from datetime import datetime

# Variable global temporal para compartir resultados
resultados_global = []

def parsear_entrada(matriz_str, vector_str):
    try:
        A = np.array([list(map(float, fila.split(','))) for fila in matriz_str.strip().split('\n')])
        b = np.array(list(map(float, vector_str.strip().split(','))))
        if A.shape[0] != A.shape[1] or A.shape[0] != b.shape[0]:
            return None, None, "La matriz A debe ser cuadrada y del mismo tamaño que el vector b."
        return A, b, None
    except Exception:
        return None, None, "Error en el formato de la matriz o vector. Usa comas y líneas como se indica."
    

def formulario_capitulo2(request):
    if request.method == 'POST':
        matriz_str = request.POST.get('matriz')
        vector_str = request.POST.get('vector')
        iteraciones = int(request.POST.get('iteraciones', 100))
        tolerancia = float(request.POST.get('tolerancia', 1e-6))
        generar_informe = request.POST.get('informe') == 'si'
        peso_sor = float(request.POST.get('peso', 1.25))

        metodos_seleccionados = request.POST.getlist('metodos')

        A, b, error = parsear_entrada(matriz_str, vector_str)
        if error:
            return render(request, 'Capitulo2/formulario_capitulo2.html', {
                "matriz": matriz_str,
                "vector": vector_str,
                "iteraciones": iteraciones,
                "tolerancia": tolerancia,
                "peso": peso_sor,
                "error": error
            })

        resultados = []
        if 'jacobi' in metodos_seleccionados:
            resultados.append(jacobi(A, b, tolerancia, iteraciones))
        if 'gs' in metodos_seleccionados:
            resultados.append(gauss_seidel(A, b, tolerancia, iteraciones))
        if 'sor' in metodos_seleccionados:
            resultados.append(sor(A, b, w=peso_sor, tol=tolerancia, max_iter=iteraciones))

        global resultados_global
        resultados_global = resultados

        return render(request, 'Capitulo2/resultados_capitulo2.html', {
            "resultados": resultados,
            "generar_informe": generar_informe
        })

    return render(request, 'Capitulo2/formulario_capitulo2.html')


def informe_capitulo2(request):
    if not resultados_global:
        return redirect('formulario_capitulo2')

    mejor = min(resultados_global, key=lambda r: (r["estado"].startswith("✅"), r["tiempo"]))
    A = np.array([list(map(float, fila.split(','))) for fila in request.POST.get("matriz", "").strip().split('\n')]) \
        if request.method == "POST" else None
    b = np.array(list(map(float, request.POST.get("vector", "").strip().split(',')))) \
        if request.method == "POST" else None

    return render(request, 'Capitulo2/informe_capitulo2.html', {
        "resultados": resultados_global,
        "mejor_metodo": mejor["nombre"],
        "radio_mejor": mejor["radio"],
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "matriz": A if A is not None else "Ver formulario",
        "vector": b if b is not None else "Ver formulario",
        "parametros": "Comparación automática con tolerancia y número de iteraciones establecidos"
    })
