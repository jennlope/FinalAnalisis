from django import forms

class InterpolacionForm(forms.Form):
    punto_eval = forms.FloatField(
        required=False,
        label="Punto para evaluar (opcional)"
    )
    y_real = forms.FloatField(
        required=True,
        label="Valor real en el punto",
        error_messages={'required': 'Debes ingresar el valor real para el informe.'}
    )
    generar_informe = forms.BooleanField(
        required=False,
        label="¿Generar informe comparativo?"
    )