from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações extras', {
            'fields': (
                'tipo_usuario',
                'telefone',
                'foto',
                'ativo',
                'coordenador_responsavel',
                'supervisor_responsavel',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações extras', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'tipo_usuario',
                'telefone',
                'foto',
                'ativo',
                'coordenador_responsavel',
                'supervisor_responsavel',
            )
        }),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'tipo_usuario',
        'coordenador_responsavel',
        'supervisor_responsavel',
        'ativo',
        'is_staff',
    )
    list_filter = ('tipo_usuario', 'ativo', 'is_staff', 'is_superuser')