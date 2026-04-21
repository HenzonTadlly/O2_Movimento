from django.contrib import admin
from .models import Membro


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone', 'idade', 'escola', 'ano_escolar', 'grupo', 'ativo')
    list_filter = ('ativo', 'escola', 'ano_escolar', 'grupo')
    search_fields = ('nome_completo', 'telefone', 'grupo__nome')