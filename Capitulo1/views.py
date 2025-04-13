from django.shortcuts import render
from .metodos import biseccion, punto_fijo, regla_falsa, secante, newton, raices_multiples

def capitulo1_view(request):
    datos = {}       # <-- Definimos datos por defecto
    resultado = None # <-- Lo mismo con resultado

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
        except Exception as e:
            resultado = {"error": f"Error durante el cálculo: {str(e)}"}

        return render(request, "resultados.html", {"datos": datos, "resultado": resultado})

    return render(request, "formulario.html", {"datos": datos})
