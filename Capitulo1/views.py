from django.shortcuts import render
from .metodos import biseccion, punto_fijo, regla_falsa, secante, newton, raices_multiples
import io
import urllib, base64
import matplotlib.pyplot as plt
import numpy as np
import math

def generar_grafica(funcion_str, a=-10, b=10, raiz_aproximada=None):
    x = np.linspace(float(a), float(b), 400)
    y = []
    for val in x:
        try:
            y.append(eval(funcion_str, {"x": val, "math": math, "np": np}))
        except:
            y.append(np.nan)

    fig, ax = plt.subplots()
    ax.plot(x, y, label="f(x)", color='blue')
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)

    if raiz_aproximada is not None:
        try:
            y_raiz = eval(funcion_str, {"x": raiz_aproximada, "math": math})
            ax.plot(raiz_aproximada, y_raiz, 'ro', label="Raíz aproximada")
        except:
            pass

    ax.set_title("Gráfica de la función")
    ax.grid(True)
    ax.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    grafica = base64.b64encode(image_png).decode("utf-8")
    plt.close()
    return grafica

def verificar_datos(metodo, datos):
    requeridos = {
        "biseccion": ["fx", "a", "b", "tol", "niter"],
        "puntofijo": ["gx", "x0", "tol", "niter"],
        "reglafalsa": ["fx", "a", "b", "tol", "niter"],
        "secante": ["fx", "x0", "x1", "tol", "niter"],
        "newton": ["fx", "dfx", "x0", "tol", "niter"],
        "multiples": ["fx", "dfx", "ddfx", "x0", "tol", "niter"],
    }
    faltantes = []
    for campo in requeridos.get(metodo, []):
        if datos.get(campo) is None:
            faltantes.append(campo)
    return faltantes

def capitulo1_view(request):
    datos = {}
    resultado = None
    grafica = None

    if request.method == "POST":
        accion = request.POST.get("accion", "calcular")
        comparar = request.POST.get("comparar", "no")

        # Si el usuario hizo clic en "Ver comparación"
        if accion == "comparar" and comparar == "si":
            return comparar_metodos(request)

        metodo = request.POST.get("metodo")
        datos = {
            "x0": request.POST.get("x0") or None,
            "tol": request.POST.get("tolerancia") or None,
            "x1": request.POST.get("x1") or None,
            "fx": request.POST.get("fx") or None,
            "gx": request.POST.get("gx") or None,
            "dfx": request.POST.get("dfx") or None,
            "niter": request.POST.get("niter") or None,
            "a": request.POST.get("a") or None,
            "b": request.POST.get("b") or None,
            "ddfx": request.POST.get("ddfx") or None,
            "metodo": metodo,
            "comparar": comparar,
        }
        try:
                faltantes = verificar_datos(metodo, datos)
                if faltantes:
                    resultado = {"error": f"Faltan los siguientes datos: {', '.join(faltantes)}"}
                else:
                    resultado = {}
                    try:
                        if metodo == "biseccion":
                            resultado = biseccion(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"])
                        elif metodo == "puntofijo":
                            resultado = punto_fijo(datos["gx"], datos["x0"], datos["tol"], datos["niter"])
                        elif metodo == "reglafalsa":
                            resultado = regla_falsa(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"])
                        elif metodo == "secante":
                            resultado = secante(datos["fx"], datos["x0"], datos["x1"], datos["tol"], datos["niter"])
                        elif metodo == "newton":
                            resultado = newton(datos["fx"], datos["dfx"], datos["x0"], datos["tol"], datos["niter"])
                        elif metodo == "multiples":
                            ddfx = request.POST.get("ddfx")
                            resultado = raices_multiples(datos["fx"], datos["dfx"], ddfx, datos["x0"], datos["tol"], datos["niter"])
                    except Exception as e:
                        resultado["error"] = f"Error durante el cálculo: {str(e)}"

                    # Intentar generar gráfica incluso si hay error
                    if datos.get("fx"):
                        try:
                            raiz_aprox = resultado.get("raiz", None)
                            a = datos.get("a") if datos.get("a") is not None else -10
                            b = datos.get("b") if datos.get("b") is not None else 10
                            grafica = generar_grafica(datos["fx"], a, b, raiz_aprox)
                        except Exception as e:
                            grafica = None
                            resultado["grafica_error"] = f"No se pudo generar la gráfica: {e}"


        except Exception as e:
            resultado = {"error": f"Error durante el cálculo: {str(e)}"}

        return render(request, "resultados.html", {
            "datos": datos,
            "resultado": resultado,
            "grafica": grafica
        })

    return render(request, "formulario.html", {"datos": datos})

def comparar_metodos(request):
    datos = {}
    resultados = {}
    metodos_eficientes = []
    min_iteraciones = float('inf')

    if request.method == "POST":
        datos = {
            "x0": request.POST.get("x0"),
            "tol": request.POST.get("tolerancia"),
            "fx": request.POST.get("fx"),
            "gx": request.POST.get("gx"),
            "dfx": request.POST.get("dfx"),
            "niter": request.POST.get("niter"),
            "a": request.POST.get("a"),
            "b": request.POST.get("b"),
            "x1": request.POST.get("x1"),
            "ddfx": request.POST.get("ddfx"),
        }

        metodos_a_probar = {
            "Bisección": lambda: biseccion(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"]),
            "Punto Fijo": lambda: punto_fijo(datos["gx"], datos["x0"], datos["tol"], datos["niter"]),
            "Regla Falsa": lambda: regla_falsa(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"]),
            "Secante": lambda: secante(datos["fx"], datos["x0"], datos["x1"], datos["tol"], datos["niter"]),
            "Newton": lambda: newton(datos["fx"], datos["dfx"], datos["x0"], datos["tol"], datos["niter"]),
            "Raíces Múltiples": lambda: raices_multiples(datos["fx"], datos["dfx"], datos["ddfx"], datos["x0"], datos["tol"], datos["niter"]),
        }

        for nombre, metodo_func in metodos_a_probar.items():
            try:
                resultado = metodo_func()
                if "resultados" in resultado:
                    iteraciones = len(resultado["resultados"])
                    resultados[nombre] = iteraciones
                    if iteraciones < min_iteraciones:
                        min_iteraciones = iteraciones
                        metodos_eficientes = [nombre]
                    elif iteraciones == min_iteraciones:
                        metodos_eficientes.append(nombre)
            except Exception as e:
                resultados[nombre] = f"Error: {str(e)}"

        # Ordenar por eficiencia (menor a mayor)
        resultados_ordenados = dict(sorted(resultados.items(), key=lambda x: x[1] if isinstance(x[1], int) else float('inf')))

        return render(request, "resultados.html", {
            "comparacion": True,
            "resultados_comparacion": resultados_ordenados,
            "mejor_metodo": ", ".join(metodos_eficientes),
            "datos": datos
        })

    return render(request, "formulario.html", {"datos": datos})