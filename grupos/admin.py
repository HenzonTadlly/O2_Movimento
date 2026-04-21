from django.contrib import admin
from .models import Grupo


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'escola', 'lider', 'supervisor', 'status', 'data_criacao')
    list_filter = ('status', 'escola')
    search_fields = ('nome', 'escola__nome', 'lider__username', 'supervisor__username')