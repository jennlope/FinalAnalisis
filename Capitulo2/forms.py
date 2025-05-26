from django import forms

METODO_CHOICES = [
    ("jacobi", "Jacobi"),
    ("gauss_seidel", "Gauss-Seidel"),
    ("sor", "SOR (requiere w)"),
]

class MetodoIterativoForm(forms.Form):
    comparar = forms.BooleanField(label="Comparar todos los métodos", required=False)
    metodo = forms.ChoiceField(label="Método", choices=METODO_CHOICES, required=False)
    dimension = forms.ChoiceField(choices=[(i, f"{i}x{i}") for i in range(2, 8)], label="Dimensión del sistema")
    tol = forms.FloatField(label="Tolerancia", min_value=1e-10)
    niter = forms.IntegerField(label="Máx. iteraciones", min_value=1)
    w1 = forms.FloatField(label="w1 (SOR)", min_value=0.1, max_value=2.0, required=False)
    w2 = forms.FloatField(label="w2 (SOR)", min_value=0.1, max_value=2.0, required=False)
    w3 = forms.FloatField(label="w3 (SOR)", min_value=0.1, max_value=2.0, required=False)
