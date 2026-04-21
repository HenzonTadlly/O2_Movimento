from django.contrib import admin
from .models import Escola


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'bairro', 'cidade', 'ativa', 'data_cadastro')
    list_filter = ('ativa', 'cidade')
    search_fields = ('nome', 'bairro', 'cidade')