from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Usuario


class BaseStyledForm:
    def apply_classes(self):
        for field_name, field in self.fields.items():
            css = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'

            current = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{current} {css}'.strip()

            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs.setdefault('placeholder', field.label)

            if field_name == 'telefone':
                field.widget.attrs.update({
                    'maxlength': '16',
                    'data-mask': 'telefone',
                    'placeholder': '(99) 99999-9999'
                })


class CriarUsuarioForm(BaseStyledForm, forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput
    )

    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'telefone',
            'tipo_usuario',
            'coordenador_responsavel',
            'supervisor_responsavel',
            'ativo',
            'password',
        ]

    def __init__(self, *args, **kwargs):
        tipo_logado = kwargs.pop('tipo_logado', None)
        usuario_logado = kwargs.pop('usuario_logado', None)
        super().__init__(*args, **kwargs)

        self.fields['coordenador_responsavel'].queryset = Usuario.objects.filter(
            tipo_usuario='coordenador',
            ativo=True
        ).order_by('first_name', 'username')

        self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
            tipo_usuario='supervisor',
            ativo=True
        ).order_by('first_name', 'username')

        self.fields['coordenador_responsavel'].required = False
        self.fields['supervisor_responsavel'].required = False

        if tipo_logado == 'supervisor':
            self.fields['tipo_usuario'].choices = [
                ('lider', 'Líder'),
            ]
            self.fields['coordenador_responsavel'].widget = forms.HiddenInput()

            if usuario_logado:
                self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
                    id=usuario_logado.id
                ).order_by('first_name', 'username')
                self.fields['supervisor_responsavel'].empty_label = "Selecione"

        elif tipo_logado == 'coordenador':
            self.fields['tipo_usuario'].choices = [
                ('supervisor', 'Supervisor'),
                ('lider', 'Líder'),
            ]

            if usuario_logado:
                self.fields['coordenador_responsavel'].queryset = Usuario.objects.filter(
                    id=usuario_logado.id
                )

                self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
                    tipo_usuario='supervisor',
                    ativo=True,
                    coordenador_responsavel=usuario_logado
                ).order_by('first_name', 'username')
                self.fields['supervisor_responsavel'].empty_label = "Selecione"

        elif tipo_logado == 'admin':
            self.fields['tipo_usuario'].choices = [
                ('coordenador', 'Coordenador'),
                ('supervisor', 'Supervisor'),
                ('lider', 'Líder'),
            ]
            self.fields['coordenador_responsavel'].empty_label = "Selecione"
            self.fields['supervisor_responsavel'].empty_label = "Selecione"

        self.apply_classes()

    def clean_first_name(self):
        value = self.cleaned_data['first_name'].strip()
        if len(value) < 2:
            raise forms.ValidationError('O nome precisa ter pelo menos 2 caracteres.')
        return value

    def clean_username(self):
        value = self.cleaned_data['username'].strip()
        if len(value) < 3:
            raise forms.ValidationError('O usuário precisa ter pelo menos 3 caracteres.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        coordenador_responsavel = cleaned_data.get('coordenador_responsavel')
        supervisor_responsavel = cleaned_data.get('supervisor_responsavel')

        if tipo_usuario == 'coordenador':
            cleaned_data['coordenador_responsavel'] = None
            cleaned_data['supervisor_responsavel'] = None

        elif tipo_usuario == 'supervisor':
            cleaned_data['supervisor_responsavel'] = None
            if not coordenador_responsavel:
                raise forms.ValidationError('Supervisor precisa ter um coordenador responsável.')

        elif tipo_usuario == 'lider':
            cleaned_data['coordenador_responsavel'] = None
            if not supervisor_responsavel:
                raise forms.ValidationError('Líder precisa ter um supervisor responsável.')

        return cleaned_data


class EditarUsuarioForm(BaseStyledForm, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'telefone',
            'coordenador_responsavel',
            'supervisor_responsavel',
            'ativo',
        ]

    def __init__(self, *args, **kwargs):
        usuario_logado = kwargs.pop('usuario_logado', None)
        super().__init__(*args, **kwargs)

        self.fields['coordenador_responsavel'].queryset = Usuario.objects.filter(
            tipo_usuario='coordenador',
            ativo=True
        ).order_by('first_name', 'username')

        self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
            tipo_usuario='supervisor',
            ativo=True
        ).order_by('first_name', 'username')

        self.fields['coordenador_responsavel'].required = False
        self.fields['supervisor_responsavel'].required = False

        if self.instance.tipo_usuario == 'coordenador':
            self.fields['coordenador_responsavel'].widget = forms.HiddenInput()
            self.fields['supervisor_responsavel'].widget = forms.HiddenInput()

        elif self.instance.tipo_usuario == 'supervisor':
            self.fields['supervisor_responsavel'].widget = forms.HiddenInput()

            if usuario_logado and usuario_logado.tipo_usuario == 'coordenador':
                self.fields['coordenador_responsavel'].queryset = Usuario.objects.filter(
                    id=usuario_logado.id
                )

        elif self.instance.tipo_usuario == 'lider':
            self.fields['coordenador_responsavel'].widget = forms.HiddenInput()

            if usuario_logado and usuario_logado.tipo_usuario == 'coordenador':
                self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
                    tipo_usuario='supervisor',
                    ativo=True,
                    coordenador_responsavel=usuario_logado
                ).order_by('first_name', 'username')

            if usuario_logado and usuario_logado.tipo_usuario == 'supervisor':
                self.fields['supervisor_responsavel'].queryset = Usuario.objects.filter(
                    id=usuario_logado.id
                ).order_by('first_name', 'username')

        self.apply_classes()

    def clean(self):
        cleaned_data = super().clean()

        if self.instance.tipo_usuario == 'supervisor':
            coordenador_responsavel = cleaned_data.get('coordenador_responsavel')
            if not coordenador_responsavel:
                raise forms.ValidationError('Supervisor precisa ter um coordenador responsável.')

        if self.instance.tipo_usuario == 'lider':
            supervisor_responsavel = cleaned_data.get('supervisor_responsavel')
            if not supervisor_responsavel:
                raise forms.ValidationError('Líder precisa ter um supervisor responsável.')

        return cleaned_data


class MeuPerfilForm(BaseStyledForm, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'telefone',
            'foto',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_classes()


class MinhaSenhaForm(BaseStyledForm, PasswordChangeForm):
    old_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_classes()