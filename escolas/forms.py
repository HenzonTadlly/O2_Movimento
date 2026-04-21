from django import forms
from .models import Escola


class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = [
            'nome',
            'bairro',
            'cidade',
            'observacao',
            'ativa',
        ]
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'

            current = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{current} {css}'.strip()

    def clean_nome(self):
        value = self.cleaned_data['nome'].strip()
        if len(value) < 3:
            raise forms.ValidationError('O nome da escola precisa ter pelo menos 3 caracteres.')
        return value