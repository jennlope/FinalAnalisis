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

def capitulo1_view(request):
    datos = {}
    resultado = None
    grafica = None

    if request.method == "POST":
        metodo = request.POST.get("metodo")
        datos = {
            "x0": request.POST.get("x0"),
            "tol": request.POST.get("tolerancia"),
            "fx": request.POST.get("fx"),
            "gx": request.POST.get("gx"),
            "dfx": request.POST.get("dfx"),
            "niter": request.POST.get("niter"),
            "a": request.POST.get("a"),
            "b": request.POST.get("b"),
            "metodo": metodo,
        }

        try:
            if metodo == "biseccion":
                resultado = biseccion(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"])
            elif metodo == "puntofijo":
                resultado = punto_fijo(datos["gx"], datos["x0"], datos["tol"], datos["niter"])
            elif metodo == "reglafalsa":
                resultado = regla_falsa(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"])
            elif metodo == "secante":
                resultado = secante(datos["fx"], datos["a"], datos["b"], datos["tol"], datos["niter"])
            elif metodo == "newton":
                resultado = newton(datos["fx"], datos["dfx"], datos["x0"], datos["tol"], datos["niter"])
            elif metodo == "multiples":
                ddfx = request.POST.get("ddfx")
                resultado = raices_multiples(datos["fx"], datos["dfx"], ddfx, datos["x0"], datos["tol"], datos["niter"])

            if datos.get("fx") and resultado and "raiz" in resultado:
                grafica = generar_grafica(datos["fx"], datos.get("a", -10), datos.get("b", 10), resultado["raiz"])

        except Exception as e:
            resultado = {"error": f"Error durante el cálculo: {str(e)}"}

        return render(request, "resultados.html", {
            "datos": datos,
            "resultado": resultado,
            "grafica": grafica
        })

    return render(request, "formulario.html", {"datos": datos})
