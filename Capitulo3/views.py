import numpy as np
import sympy as sp
import matplotlib
matplotlib.use('Agg')  # Usar backend para generación de imágenes sin GUI
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
        indices_ordenados = np.argsort(x)
        x = x[indices_ordenados]
        y = y[indices_ordenados]
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
        try:
            plt.style.use('seaborn-v0_8')  # compatible con versiones recientes
        except:
            plt.style.use('default')  # fallback
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
    polinomios_str = {}

    if datos_para_informe and datos_para_informe.get("punto_eval") is not None:
        # --- Lectura y ordenamiento de datos ---
        x = np.array(datos_para_informe["x"])
        y = np.array(datos_para_informe["y"])
        x_eval = datos_para_informe["punto_eval"]

        orden = np.argsort(x)
        x = x[orden]
        y = y[orden]

        # --- Cálculo del valor "real" (interp. lineal/extrap.) ---
        def real_val(xe):
            if xe <= x[0]:
                i = 0
            elif xe >= x[-1]:
                i = len(x) - 2
            else:
                for j in range(len(x) - 1):
                    if x[j] <= xe <= x[j+1]:
                        i = j
                        break
            xi, xf = x[i], x[i+1]
            yi, yf = y[i], y[i+1]
            return yi + (yf - yi)/(xf - xi)*(xe - xi)

        y_real = real_val(x_eval)
        if x_eval < x[0]:
            metodo_real = f"Extrapolación (izquierda fuera del dominio [{x[0]}, {x[-1]}])"
        elif x_eval > x[-1]:
            metodo_real = f"Extrapolación (derecha fuera del dominio [{x[0]}, {x[-1]}])"
        else:
            metodo_real = "Interpolación dentro del dominio"

        # --- Métodos polinómicos: Vandermonde, Lagrange, Newton ---
        for metodo in ["vandermonde", "lagrange", "newton"]:
            pol = datos_para_informe[metodo]

            # 1) Generar cadena del polinomio (simplificado y expandido)
            pol_simple = sp.expand(sp.simplify(pol))
            pol_str = str(pol_simple)
            polinomios_str[metodo] = pol_str

            # 2) Evaluar y calcular error
            y_aprox = float(pol.evalf(subs={x_sym: x_eval}))
            error = abs(y_real - y_aprox)
            informe[metodo.capitalize()] = {
                "aproximado": y_aprox,
                "real":      y_real,
                "error":     error
            }

        # --- Spline Lineal ---
        from Capitulo3.utils import spline_lineal
        spl = spline_lineal(x, y)
        y_aprox_spline = None
        for (s, (xi, xf)) in spl:
            if xi <= x_eval <= xf:
                y_aprox_spline = float(s.evalf(subs={x_sym: x_eval}))
                break
        if y_aprox_spline is None:
            s, _ = (spl[0] if x_eval < x[0] else spl[-1])
            y_aprox_spline = float(s.evalf(subs={x_sym: x_eval}))
        error = abs(y_real - y_aprox_spline)
        informe["Spline Lineal"] = {
            "aproximado": y_aprox_spline,
            "real":       y_real,
            "error":      error
        }

        # --- Spline Cúbico ---
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(x, y, extrapolate=True)
        y_aprox_cu = cs(x_eval)
        error = abs(y_real - y_aprox_cu)
        informe["Spline Cúbico"] = {
            "aproximado": float(y_aprox_cu),
            "real":       y_real,
            "error":      error
        }
        # Guardar también los polinomios de los splines en formato de texto para mostrar
        spl_strs = []
        for s, inter in spl:
            intervalo = f"[{inter[0]}, {inter[1]}]"
            spl_strs.append((str(s), intervalo))

        # CubicSpline no tiene forma simbólica directa, así que lo mostramos como coeficientes por tramo
        spl_cu_strs = []
        for i in range(len(x) - 1):
            coefs = cs.c[:, i]  # Los coeficientes vienen como columnas
            expr_parts = []
            potencias = [3, 2, 1, 0]
            for j in range(len(coefs)):
                coef = coefs[j]
                potencia = potencias[j]
                if abs(coef) > 1e-12:  # Evita imprimir términos insignificantes
                    if potencia == 0:
                        expr_parts.append(f"{coef:.3f}")
                    elif potencia == 1:
                        expr_parts.append(f"{coef:.3f}(x - {x[i]})")
                    else:
                        expr_parts.append(f"{coef:.3f}(x - {x[i]})^{potencia}")
            expr = " + ".join(expr_parts)
            intervalo = f"[{x[i]}, {x[i+1]}]"
            spl_cu_strs.append((expr, intervalo))


        # --- Render con polinomios en el contexto ---
        return render(request, "Capitulo3/informe.html", {
        "informe":                  informe,
        "punto_eval":               x_eval,
        "metodo_real":              metodo_real,
        "polinomio_vandermonde":    polinomios_str["vandermonde"],
        "polinomio_lagrange":       polinomios_str["lagrange"],
        "polinomio_newton":         polinomios_str["newton"],
        "splines_lineales":         spl_strs,
        "splines_cubicos":          spl_cu_strs,
        })


    # Si no hay punto de evaluación, sólo muestra el formulario vacío
    return render(request, "Capitulo3/informe.html", {
        "punto_eval": None
    })