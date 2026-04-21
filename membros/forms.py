from django import forms
from .models import Membro


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = [
            'nome_completo',
            'telefone',
            'idade',
            'escola',
            'ano_escolar',
            'ativo',
            'observacao',
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

        self.fields['telefone'].widget.attrs.update({
            'maxlength': '16',
            'data-mask': 'telefone',
            'placeholder': '(99) 99999-9999'
        })

        self.fields['idade'].widget.attrs.update({
            'min': '1',
            'max': '120',
            'placeholder': 'Idade'
        })

    def clean_nome_completo(self):
        value = self.cleaned_data['nome_completo'].strip()
        if len(value) < 5:
            raise forms.ValidationError('Digite o nome completo do membro.')
        return value

    def clean_idade(self):
        idade = self.cleaned_data['idade']
        if idade < 1 or idade > 120:
            raise forms.ValidationError('Digite uma idade válida.')
        return idade

    def clean_ano_escolar(self):
        value = self.cleaned_data['ano_escolar'].strip()
        if len(value) < 1:
            raise forms.ValidationError('Informe o ano escolar.')
        return value