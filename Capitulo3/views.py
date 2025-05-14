import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import io, base64
from django.shortcuts import render
from .forms import InterpolacionForm
from .utils import vandermonde, lagrange, newton_divididas, spline_lineal, spline_cubico

# Variable temporal para almacenar datos del informe
datos_para_informe = {}

def formulario_interpolacion(request):
    form = InterpolacionForm()
    return render(request, "Capitulo3/formulario.html", {
        "form": form,
        "rango": range(8)
    })

def resultado_interpolacion(request):
    global datos_para_informe
    
    if request.method == "POST":
        form = InterpolacionForm(request.POST)
        metodo = request.POST.get("metodo")

        # Validación básica del método
        if not metodo:
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "Debes seleccionar un método de interpolación."
            })

        try:
            # Procesamiento de datos de entrada
            x_vals = list(map(float, [v for k, v in request.POST.items() if k.startswith('x') and v != '']))
            y_vals = list(map(float, [v for k, v in request.POST.items() if k.startswith('y') and v != '']))
        except ValueError:
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "Todos los valores de x e y deben ser números válidos."
            })

        # Validación de datos
        if len(x_vals) != len(y_vals):
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "El número de valores en x e y debe coincidir."
            })

        if len(x_vals) < 2:
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "Debes ingresar al menos 2 puntos."
            })

        if len(set(x_vals)) != len(x_vals):
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "Los valores de x deben ser únicos (no repetidos)."
            })

        # Procesar punto de evaluación
        punto_eval = request.POST.get("punto_eval")
        try:
            punto_eval = float(punto_eval) if punto_eval else None
        except ValueError:
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": "El punto de evaluación debe ser numérico."
            })

        generar_informe = 'generar_informe' in request.POST

        # Preparación de datos
        x = np.array(x_vals)
        y = np.array(y_vals)
        resultado = {}
        x_sym = sp.Symbol('x')

        try:
            # Aplicar el método seleccionado
            if metodo == "vandermonde":
                pol, _ = vandermonde(x, y)
                resultado["vandermonde"] = sp.pretty(pol, use_unicode=False)
                y_plot = [float(pol.evalf(subs={x_sym: val})) for val in x]
            elif metodo == "lagrange":
                pol = lagrange(x, y)
                resultado["lagrange"] = sp.pretty(pol, use_unicode=False)
                y_plot = [float(pol.evalf(subs={x_sym: val})) for val in x]
            elif metodo == "newton":
                pol, _ = newton_divididas(x, y)
                resultado["newton"] = sp.pretty(pol, use_unicode=False)
                y_plot = [float(pol.evalf(subs={x_sym: val})) for val in x]
            elif metodo == "spline_lineal":
                spl_l = spline_lineal(x, y)
                resultado["splines_lineales"] = spl_l
                y_plot = None
            elif metodo == "spline_cubico":
                spl_c = spline_cubico(x, y)
                resultado["splines_cubicos"] = spl_c
                y_plot = None
            else:
                raise ValueError("Método no válido")
        except Exception as e:
            return render(request, "Capitulo3/formulario.html", {
                "form": form,
                "rango": range(8),
                "error": f"Error al calcular: {str(e)}"
         })

        # Configuración de la gráfica
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Estilos por método
        method_styles = {
            "vandermonde": ("blue", "-", "Polinomio (Vandermonde)"),
            "lagrange": ("green", "--", "Polinomio (Lagrange)"),
            "newton": ("purple", ":", "Polinomio (Newton)"),
            "spline_lineal": ("orange", "-", "Spline Lineal"),
            "spline_cubico": ("red", "-", "Spline Cúbico")
        }
        
        color, linestyle, label = method_styles[metodo]
        
        # Graficar puntos de datos
        ax.plot(x, y, 'ro', markersize=8, label='Puntos de datos', zorder=3)
        
        # Graficar según el método
        if metodo in ["vandermonde", "lagrange", "newton"]:
            x_range = max(x) - min(x)
            x_plot = np.linspace(min(x) - 0.1*x_range, max(x) + 0.1*x_range, 500)
            y_plot = [float(pol.evalf(subs={x_sym: xi})) for xi in x_plot]
            ax.plot(x_plot, y_plot, color=color, linestyle=linestyle, label=label, linewidth=2)
            
            # Destacar punto evaluado si existe
            if punto_eval and min(x) <= punto_eval <= max(x):
                y_eval = float(pol.evalf(subs={x_sym: punto_eval}))
                ax.plot(punto_eval, y_eval, 'ks', markersize=8, label=f'Evaluación (x={punto_eval:.2f})')
                
        elif metodo == "spline_lineal":
            for i in range(len(x)-1):
                x_seg = [x[i], x[i+1]]
                y_seg = [y[i], y[i+1]]
                ax.plot(x_seg, y_seg, color=color, linestyle=linestyle, 
                       label=label if i==0 else "", linewidth=2)
                
        elif metodo == "spline_cubico":
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(x, y)
            x_plot = np.linspace(min(x), max(x), 500)
            ax.plot(x_plot, cs(x_plot), color=color, linestyle=linestyle, 
                   label=label, linewidth=2)
        
        # Configuración estética del gráfico
        ax.set_title(f'Interpolación usando método {metodo.capitalize()}', fontsize=14)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=10, loc='best')
        plt.tight_layout()
        
        # Convertir gráfica a base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        grafica = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()

        # Almacenar datos para posible informe
        datos_para_informe = {
            "x": x.tolist(),
            "y": y.tolist(),
            "punto_eval": punto_eval,
            "vandermonde": vandermonde(x, y)[0],
            "lagrange": lagrange(x, y),
            "newton": newton_divididas(x, y)[0],
            "metodo_usado": metodo
        }

        return render(request, "Capitulo3/resultados.html", {
            "resultado": resultado,
            "grafica": grafica,
            "punto_eval": punto_eval,
            "generar_informe": generar_informe,
            "metodo": metodo
        })

    return render(request, "Capitulo3/formulario.html", {
        "form": InterpolacionForm(),
        "rango": range(8)
    })
    
def generar_informe(request):
    global datos_para_informe
    x_sym = sp.Symbol('x')
    informe = {}

    if datos_para_informe and datos_para_informe.get("punto_eval") is not None:
        x = datos_para_informe["x"]
        y = datos_para_informe["y"]
        x_eval = datos_para_informe["punto_eval"]

        def real_val(x_eval):
            for i in range(len(x) - 1):
                if x[i] <= x_eval <= x[i+1]:
                    return y[i] + (y[i+1] - y[i]) / (x[i+1] - x[i]) * (x_eval - x[i])
            return None

        y_real = real_val(x_eval)

        for metodo in ["vandermonde", "lagrange", "newton"]:
            pol = datos_para_informe[metodo]
            y_aprox = float(pol.evalf(subs={x_sym: x_eval}))
            error = abs(y_real - y_aprox) if y_real is not None else "N/A"
            informe[metodo.capitalize()] = {
                "aproximado": y_aprox,
                "real": y_real,
                "error": error
            }

        return render(request, "Capitulo3/informe.html", {
            "informe": informe,
            "punto_eval": x_eval
        })

    return render(request, "Capitulo3/informe.html", {"punto_eval": None})
