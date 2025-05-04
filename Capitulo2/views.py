import numpy as np
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .metodos_capitulo2 import jacobi, gauss_seidel, sor, comparar_metodos

def capitulo2_form(request):
    """Renderiza el formulario de entrada"""
    return render(request, 'Capitulo2/formulario_capitulo2.html')

@require_POST
def calcular_resultados(request):
    """Procesa los datos del formulario"""
    try:
        # 1. Extraer tamaño de la matriz
        size = int(request.POST.get('matrixSize', 3))
        
        # 2. Construir matriz A y vector b
        A = np.zeros((size, size))
        b = np.zeros(size)
        for i in range(size):
            for j in range(size):
                A[i][j] = float(request.POST.get(f'A_{i}_{j}'))
            b[i] = float(request.POST.get(f'b_{i}'))
        
        # 3. Parámetros numéricos
        tol = float(request.POST.get('tolerancia', 1e-6))
        niter = int(request.POST.get('niter', 50))
        omega = float(request.POST.get('omega', 1.5))
        x0 = np.zeros(size)  # Vector inicial
        
        # 4. Ejecutar métodos seleccionados
        metodos_seleccionados = request.POST.getlist('metodos')
        resultados = {}
        
        if 'jacobi' in metodos_seleccionados:
            resultados['jacobi'] = jacobi(A, b, x0, tol, niter)
        
        if 'gauss_seidel' in metodos_seleccionados:
            resultados['gauss_seidel'] = gauss_seidel(A, b, x0, tol, niter)
        
        if 'sor' in metodos_seleccionados:
            resultados['sor'] = sor(A, b, x0, omega, tol, niter)
        
        # 5. Guardar en sesión para el informe
        request.session['resultados'] = {
            'A': A.tolist(),
            'b': b.tolist(),
            'metodos': resultados,
            'params': {'tol': tol, 'niter': niter, 'omega': omega}
        }
        
        # 6. Redireccionar según sea necesario
        if len(metodos_seleccionados) == 1:
            return render(request, 'Capitulo2/resultados_capitulo2.html', {
                'metodo': metodos_seleccionados[0],
                'resultado': resultados[metodos_seleccionados[0]],
                'generar_informe': request.POST.get('generar_informe') == 'si'
            })
        
        else:
            if request.POST.get('generar_informe') == 'si':
                return redirect('generar_informe')
            else:
                # Redirige a resultados con el primer método
                return render(request, 'Capitulo2/resultados_capitulo2.html', {
                    'metodo': metodos_seleccionados[0],
                    'resultado': resultados[metodos_seleccionados[0]],
                    'otros_resultados': {k:v for k,v in resultados.items() if k != metodos_seleccionados[0]},
                    'generar_informe': False
                })

    except Exception as e:
        # Asegúrate de pasar el error al template
        return render(request, 'Capitulo2/formulario_capitulo2.html', {
            'error': f"Error en los datos: {str(e)}",
            'form_data': request.POST  # Para mantener los datos ingresados
        })

def generar_informe(request):
    """Genera el informe comparativo"""
    data = request.session.get('resultados', {})
    if not data:
        return redirect('capitulo2_form')
    
    resultados = data['metodos']
    mejor_metodo = min(
        resultados.items(),
        key=lambda item: len(item[1]['resultados'])
    )
    
    return render(request, 'Capitulo2/informe_capitulo2.html', {
        'resultados': resultados,
        'mejor_metodo': mejor_metodo[0],
        'mejor_solucion': mejor_metodo[1]['solucion'],
        'matriz_A': data['A'],
        'vector_b': data['b'],
        'params': data['params']
    })