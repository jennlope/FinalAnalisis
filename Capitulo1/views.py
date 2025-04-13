from django.shortcuts import render

# Create your views here.
def capitulo1_view(request):
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
        return render(request, "resultados.html", {"datos": datos})
    return render(request, "formulario.html")
