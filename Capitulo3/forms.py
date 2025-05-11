from django import forms

class InterpolacionForm(forms.Form):
    x_vals = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), label="Valores de x (separados por comas)")
    y_vals = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), label="Valores de y (separados por comas)")
    punto_eval = forms.FloatField(required=False, label="Punto para evaluar (opcional)")
    generar_informe = forms.BooleanField(required=False, label="¿Generar informe comparativo?")
