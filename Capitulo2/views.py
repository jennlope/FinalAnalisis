from django.shortcuts import render
from .forms import MetodoIterativoForm
from .utils import jacobi, gauss_seidel, sor

# Create your views here.
def formulario_capitulo2(request):
    form = MetodoIterativoForm()
    return render(request, 'Capitulo2/formulario.html', {
        "form": form,
        "rango": range(7)  # para generar dinámicamente inputs hasta 7x7
    })

def resultado_capitulo2(request):
    form = MetodoIterativoForm(request.POST or None)
    comparar = request.POST.get("comparar") == "on"
    metodo = request.POST.get("metodo")

    # Validar que el usuario haya seleccionado un método si no compara
    if request.method == "POST" and not comparar and not metodo:
        return render(request, "Capitulo2/formulario.html", {
            "form": form,
            "error": "Debes seleccionar un método o activar comparación.",
            "rango": range(7)
        })

    if request.method == "POST" and form.is_valid():
        dim = int(form.cleaned_data["dimension"])
        try:
            A = [[float(request.POST.get(f"A{i}{j}")) for j in range(dim)] for i in range(dim)]
            b = [float(request.POST.get(f"b{i}")) for i in range(dim)]
            x0 = [float(request.POST.get(f"x0{i}")) for i in range(dim)]
        except (ValueError, TypeError):
            return render(request, "Capitulo2/formulario.html", {
                "form": form,
                "error": "Todos los campos deben estar llenos y contener solo números.",
                "rango": range(7)
            })

        tol = form.cleaned_data["tol"]
        niter = form.cleaned_data["niter"]
        w1 = form.cleaned_data["w1"]
        w2 = form.cleaned_data["w2"]
        w3 = form.cleaned_data["w3"]

        # Extraer matrices y vectores
        A = [[float(request.POST.get(f"A{i}{j}")) for j in range(dim)] for i in range(dim)]
        b = [float(request.POST.get(f"b{i}")) for i in range(dim)]
        x0 = [float(request.POST.get(f"x0{i}")) for i in range(dim)]

        # Ejecutar métodos
        res_jacobi = jacobi(A, b, x0, tol, niter) if comparar or metodo == "jacobi" else None
        res_gauss = gauss_seidel(A, b, x0, tol, niter) if comparar or metodo == "gauss_seidel" else None
        res_sor1 = sor(A, b, x0, tol, niter, w1) if comparar or metodo == "sor" else None
        res_sor2 = sor(A, b, x0, tol, niter, w2) if comparar else None
        res_sor3 = sor(A, b, x0, tol, niter, w3) if comparar else None

        # Comparación
        metodos = {}
        if res_jacobi: metodos["Jacobi"] = res_jacobi
        if res_gauss: metodos["Gauss-Seidel"] = res_gauss
        if res_sor1: metodos[f"SOR (w={w1})"] = res_sor1
        if res_sor2: metodos[f"SOR (w={w2})"] = res_sor2
        if res_sor3: metodos[f"SOR (w={w3})"] = res_sor3

        if not metodos:
            return render(request, "Capitulo2/formulario.html", {
                "form": MetodoIterativoForm(),
                "error": "No se ejecutó ningún método válido.",
                "rango": range(7)
            })

        mejor = min(metodos.items(), key=lambda item: item[1][-1][-1]) if comparar else None

        # Definir el método elegido solo si no es comparación
        if metodo == "jacobi":
            metodo_elegido = "Jacobi"
        elif metodo == "gauss_seidel":
            metodo_elegido = "Gauss-Seidel"
        elif metodo == "sor":
                metodo_elegido = "SOR"
        else:
            metodo_elegido = None

        return render(request, "Capitulo2/resultado.html", {
            "comparar": comparar,
            "res_jacobi": res_jacobi,
            "res_gauss": res_gauss,
            "res_sor1": res_sor1,
            "res_sor2": res_sor2,
            "res_sor3": res_sor3,
            "mejor": mejor[0] if mejor else None,
            "resultado_final": metodos if comparar else None,
            "metodo_elegido": metodo_elegido,
            "request": request,
        })

    # GET o POST inválido
    return render(request, "Capitulo2/formulario.html", {
        "form": form,
        "error": "Datos inválidos.",
        "rango": range(7)
    })

def informe_capitulo2(request):
    if request.method == "POST":
        form = MetodoIterativoForm(request.POST)
        if form.is_valid():
            dim = int(form.cleaned_data["dimension"])
            try:
                A = [[float(request.POST.get(f"A{i}{j}")) for j in range(dim)] for i in range(dim)]
                b = [float(request.POST.get(f"b{i}")) for i in range(dim)]
                x0 = [float(request.POST.get(f"x0{i}")) for i in range(dim)]
            except (ValueError, TypeError):
                return render(request, "Capitulo2/formulario.html", {
                    "form": form,
                    "error": "Todos los campos deben estar llenos y contener solo números.",
                    "rango": range(7)
                })

            tol = form.cleaned_data["tol"]
            niter = form.cleaned_data["niter"]
            w1 = form.cleaned_data["w1"]
            w2 = form.cleaned_data["w2"]
            w3 = form.cleaned_data["w3"]

            A = [[float(request.POST.get(f"A{i}{j}")) for j in range(dim)] for i in range(dim)]
            b = [float(request.POST.get(f"b{i}")) for i in range(dim)]
            x0 = [float(request.POST.get(f"x0{i}")) for i in range(dim)]

            metodos = {
                "Jacobi": jacobi(A, b, x0, tol, niter),
                "Gauss-Seidel": gauss_seidel(A, b, x0, tol, niter),
                f"SOR (w={w1})": sor(A, b, x0, tol, niter, w1),
                f"SOR (w={w2})": sor(A, b, x0, tol, niter, w2),
                f"SOR (w={w3})": sor(A, b, x0, tol, niter, w3),
            }

            resumen = []
            for nombre, resultado in metodos.items():
                iteraciones = resultado[-1][0]
                solucion = resultado[-1][1:-1]
                error = resultado[-1][-1]
                resumen.append({
                    "metodo": nombre,
                    "niter": iteraciones,
                    "solucion": solucion,
                    "error": error,
                })

            # Elegir mejor método: menor error
            mejor_metodo = min(resumen, key=lambda r: r["error"])

            return render(request, "Capitulo2/informe.html", {
                "resumen": resumen,
                "mejor": mejor_metodo["metodo"],
            })

    return render(request, "Capitulo2/formulario.html", {"form": MetodoIterativoForm(), "error": "Datos inválidos"})