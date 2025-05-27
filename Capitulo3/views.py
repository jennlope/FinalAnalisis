# Capitulo3/views.py
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

from django.shortcuts import render
from .forms import InterpolacionForm
from .utils import vandermonde, lagrange, newton_divididas, spline_lineal

datos_para_informe = {}

def formulario_interpolacion(request):
    form = InterpolacionForm()
    return render(request, "Capitulo3/formulario.html", {
        "form": form,
        "rango": range(8)
    })

def resultado_interpolacion(request):
    global datos_para_informe

    if request.method != "POST":
        return formulario_interpolacion(request)

    form = InterpolacionForm(request.POST)
    if not form.is_valid():
        # Si falla validación de punto_eval / y_real
        return render(request, "Capitulo3/formulario.html", {
            "form": form,
            "rango": range(8)
        })

    metodo = request.POST.get("metodo")
    if not metodo:
        form.add_error(None, "Debes seleccionar un método de interpolación.")
        return render(request, "Capitulo3/formulario.html", {
            "form": form,
            "rango": range(8)
        })

    # --- Extraer los puntos x0…x7, y0…y7 ---
    x_vals, y_vals = [], []
    for i in range(8):
        xv = request.POST.get(f"x{i}", "").strip()
        yv = request.POST.get(f"y{i}", "").strip()
        if xv or yv:
            if not (xv and yv):
                form.add_error(None, f"Fila {i+1}: debes ingresar ambos valores X y Y o dejarlos vacíos.")
                return render(request, "Capitulo3/formulario.html", {
                    "form": form,
                    "rango": range(8)
                })
            try:
                x_vals.append(float(xv))
                y_vals.append(float(yv))
            except ValueError:
                form.add_error(None, f"Entrada inválida en fila {i+1}: X e Y deben ser números.")
                return render(request, "Capitulo3/formulario.html", {
                    "form": form,
                    "rango": range(8)
                })

    if len(x_vals) < 2:
        form.add_error(None, "Debes ingresar al menos 2 puntos.")
        return render(request, "Capitulo3/formulario.html", {
            "form": form,
            "rango": range(8)
        })

    if len(x_vals) != len(y_vals):
        form.add_error(None, "El número de valores en x e y debe coincidir.")
        return render(request, "Capitulo3/formulario.html", {
            "form": form,
            "rango": range(8)
        })

    if len(set(x_vals)) != len(x_vals):
        form.add_error(None, "Los valores de x deben ser únicos (no repetidos).")
        return render(request, "Capitulo3/formulario.html", {
            "form": form,
            "rango": range(8)
        })

    # Ya validado punto_eval y y_real
    punto_eval = form.cleaned_data["punto_eval"]
    y_real     = form.cleaned_data["y_real"]
    generar_informe = form.cleaned_data["generar_informe"]

    # Ordenar
    x = np.array(x_vals)
    y = np.array(y_vals)
    idx = np.argsort(x)
    x, y = x[idx], y[idx]

    x_sym = sp.Symbol('x')
    resultado = {}
    polynomial_objs = {}

    # ---- Cálculo del polinomio o splines ----
    if metodo == "vandermonde":
        try:
            pol, _ = vandermonde(x, y)
            polynomial_objs["vandermonde"] = pol
            resultado["vandermonde"] = sp.pretty(pol, use_unicode=False)
        except Exception as e:
            resultado["vandermonde"] = f"Error: {e}"

    elif metodo == "lagrange":
        try:
            pol = lagrange(x, y)
            polynomial_objs["lagrange"] = pol
            resultado["lagrange"] = sp.pretty(pol, use_unicode=False)
        except Exception as e:
            resultado["lagrange"] = f"Error: {e}"

    elif metodo == "newton":
        try:
            pol, _ = newton_divididas(x, y)
            polynomial_objs["newton"] = pol
            resultado["newton"] = sp.pretty(pol, use_unicode=False)
        except Exception as e:
            resultado["newton"] = f"Error: {e}"

    elif metodo == "spline_lineal":
        try:
            spl = spline_lineal(x, y)
            resultado["splines_lineales"] = spl
        except Exception as e:
            resultado["splines_lineales"] = f"Error: {e}"

    elif metodo == "spline_cubico":
        try:
            from scipy.interpolate import CubicSpline
            spl_cu = CubicSpline(x, y)
            resultado["splines_cubicos"] = spl_cu  # guardamos el objeto
        except ImportError:
            resultado["splines_cubicos"] = "Error: SciPy no está disponible."
        except Exception as e:
            resultado["splines_cubicos"] = f"Error: {e}"

    else:
        resultado["error"] = "Método no reconocido."

    # ---- Gráfica siempre muestra los puntos; añado polinomio o spline si no hubo error ----
    try:
        plt.style.use('seaborn-v0_8')
    except:
        pass
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, 'ro', markersize=6, label='Puntos de datos', zorder=3)

    # Polinomios
    if metodo in ("vandermonde","lagrange","newton") and metodo in polynomial_objs:
        pol = polynomial_objs[metodo]
        x_plot = np.linspace(x.min(), x.max(), 300)
        y_plot = [float(pol.evalf(subs={x_sym: xi})) for xi in x_plot]
        ax.plot(x_plot, y_plot, label=f"Polinomio ({metodo.capitalize()})", linewidth=2)

        if punto_eval is not None and x.min() <= punto_eval <= x.max():
            y_e = float(pol.evalf(subs={x_sym: punto_eval}))
            ax.plot(punto_eval, y_e, 'ks', label=f"f({punto_eval})={y_e:.3f}")

    # Spline lineal
    if metodo=="spline_lineal" and isinstance(resultado.get("splines_lineales"), list):
        for i in range(len(x)-1):
            xi, xf = x[i], x[i+1]
            yi, yf = y[i], y[i+1]
            ax.plot([xi,xf],[yi,yf], label="Spline lineal" if i==0 else "", linewidth=2)

    # Spline cúbico
    if metodo=="spline_cubico" and not isinstance(resultado.get("splines_cubicos"), str):
        cs = resultado["splines_cubicos"]
        x_plot = np.linspace(x.min(), x.max(), 300)
        ax.plot(x_plot, cs(x_plot), label="Spline cúbico", linewidth=2)

    ax.set_title(f"Interpolación ({metodo.capitalize()})", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)

    # Guardar para informe
    datos_para_informe = {
        "x": x.tolist(),
        "y": y.tolist(),
        "punto_eval": punto_eval,
        "y_real": y_real,
        "polynomial_objs": polynomial_objs,
        "metodo_usado": metodo
    }

    return render(request, "Capitulo3/resultados.html", {
        "resultado": resultado,
        "grafica": img_b64,
        "punto_eval": punto_eval,
        "generar_informe": generar_informe,
        "metodo": metodo,
    })

def generar_informe(request):
    global datos_para_informe
    if not datos_para_informe:
        return render(request, "Capitulo3/informe.html", {"punto_eval": None})

    x = np.array(datos_para_informe["x"])
    y = np.array(datos_para_informe["y"])
    x_eval = datos_para_informe["punto_eval"]
    y_real = datos_para_informe["y_real"]
    objs = datos_para_informe["polynomial_objs"]
    x_sym = sp.Symbol('x')

    informe = {}
    pol_strs = {}

    # Polinomios
    for key in ("vandermonde","lagrange","newton"):
        pol = objs.get(key)
        if pol is not None:
            try:
                psim = sp.expand(sp.simplify(pol))
                pol_strs[key] = str(psim)
                y_ap = float(pol.evalf(subs={x_sym: x_eval}))
                err = abs(y_real - y_ap)
                informe[key.capitalize()] = {
                    "aproximado": y_ap,
                    "real": y_real,
                    "error": err
                }
            except Exception as e:
                informe[key.capitalize()] = {
                    "aproximado": "Error",
                    "real": y_real,
                    "error": f"{e}"
                }
                pol_strs[key] = f"Error: {e}"
        else:
            pol_strs[key] = "No calculado"

    # Spline lineal
    from .utils import spline_lineal
    try:
        spl = spline_lineal(x, y)
        y_ap = next(
            float(s.evalf(subs={x_sym: x_eval}))
            for s,(xi,xf) in spl
            if xi <= x_eval <= xf
        )
        informe["Spline Lineal"] = {
            "aproximado": y_ap,
            "real": y_real,
            "error": abs(y_real - y_ap)
        }
        splines_lineales = [(str(s), f"[{a}, {b}]") for s,(a,b) in spl]
    except Exception as e:
        informe["Spline Lineal"] = {
            "aproximado": "Error",
            "real": y_real,
            "error": f"{e}"
        }
        splines_lineales = []

    # Spline cúbico
    try:
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(x, y, extrapolate=True)
        y_ap = float(cs(x_eval))
        informe["Spline Cúbico"] = {
            "aproximado": y_ap,
            "real": y_real,
            "error": abs(y_real - y_ap)
        }
        coefs = cs.c
        spl_cub = []
        for i in range(len(x)-1):
            c = coefs[:, i]
            expr = " + ".join(f"{float(c[j]):.3f}*(x - {x[i]})**{3-j}" 
                               for j in range(4) if abs(c[j])>1e-12)
            spl_cub.append((expr, f"[{x[i]}, {x[i+1]}]"))
    except Exception as e:
        informe["Spline Cúbico"] = {
            "aproximado": "Error",
            "real": y_real,
            "error": f"{e}"
        }
        spl_cub = []

    # Mejor(es) método(s)
    numeric = [(m, d["error"]) for m,d in informe.items() if isinstance(d["error"], (int,float))]
    if numeric:
        min_e = min(e for _,e in numeric)
        mejores = [m for m,e in numeric if abs(e-min_e)<1e-8]
    else:
        mejores = []

    return render(request, "Capitulo3/informe.html", {
        "informe": informe,
        "punto_eval": x_eval,
        "metodo_real": "Ingresado manualmente",
        "polinomio_vandermonde": pol_strs["vandermonde"],
        "polinomio_lagrange":    pol_strs["lagrange"],
        "polinomio_newton":      pol_strs["newton"],
        "splines_lineales":      splines_lineales,
        "splines_cubicos":       spl_cub,
        "mejores_metodos":       mejores,
    })