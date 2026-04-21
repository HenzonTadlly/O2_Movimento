from django import forms
from django.utils import timezone


class LancarFrequenciaForm(forms.Form):
    data_encontro = forms.DateField(
        label='Data do encontro',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    observacao = forms.CharField(
        label='Observação',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Opcional'
        })
    )

    def clean_data_encontro(self):
        data_encontro = self.cleaned_data['data_encontro']
        hoje = timezone.localdate()

        if data_encontro.year < 2020:
            raise forms.ValidationError('Informe uma data válida.')

        if data_encontro > hoje:
            raise forms.ValidationError('A data do encontro não pode ser no futuro.')

        return data_encontro

    def clean_observacao(self):
        observacao = self.cleaned_data.get('observacao', '').strip()
        if len(observacao) > 500:
            raise forms.ValidationError('A observação pode ter no máximo 500 caracteres.')
        return observacao