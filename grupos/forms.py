from django import forms
from .models import Grupo
from escolas.models import Escola
from usuarios.models import Usuario


class GrupoForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(tipo_usuario='supervisor', ativo=True).order_by('first_name', 'username'),
        required=False
    )

    class Meta:
        model = Grupo
        fields = ['nome', 'escola', 'lider', 'supervisor', 'status', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        usuario_logado = kwargs.pop('usuario_logado', None)
        super().__init__(*args, **kwargs)

        self.fields['escola'].queryset = Escola.objects.filter(ativa=True).order_by('nome')
        self.fields['lider'].queryset = Usuario.objects.filter(
            tipo_usuario='lider',
            ativo=True
        ).order_by('first_name', 'username')

        if usuario_logado and usuario_logado.tipo_usuario == 'supervisor':
            self.fields['supervisor'].widget = forms.HiddenInput()
            self.fields['supervisor'].required = False
            self.fields['lider'].queryset = Usuario.objects.filter(
                tipo_usuario='lider',
                ativo=True,
                supervisor_responsavel=usuario_logado
            ).order_by('first_name', 'username')

        elif usuario_logado and usuario_logado.tipo_usuario == 'coordenador':
            self.fields['supervisor'].queryset = Usuario.objects.filter(
                tipo_usuario='supervisor',
                ativo=True,
                coordenador_responsavel=usuario_logado
            ).order_by('first_name', 'username')

            self.fields['lider'].queryset = Usuario.objects.filter(
                tipo_usuario='lider',
                ativo=True,
                supervisor_responsavel__coordenador_responsavel=usuario_logado
            ).order_by('first_name', 'username')

        for field_name, field in self.fields.items():
            css = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'

            current = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{current} {css}'.strip()

    def clean_nome(self):
        value = self.cleaned_data['nome'].strip()
        if len(value) < 3:
            raise forms.ValidationError('O nome do grupo precisa ter pelo menos 3 caracteres.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        lider = cleaned_data.get('lider')
        supervisor = cleaned_data.get('supervisor')

        if lider and supervisor and lider.supervisor_responsavel != supervisor:
            raise forms.ValidationError('O líder escolhido não está vinculado a esse supervisor.')

        return cleaned_data