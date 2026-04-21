from django.contrib import admin
from .models import Encontro, Frequencia


@admin.register(Encontro)
class EncontroAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'data_encontro', 'criado_por')
    list_filter = ('grupo', 'data_encontro')
    search_fields = ('grupo__nome',)


@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('encontro', 'membro', 'presente')
    list_filter = ('presente', 'encontro__grupo')
    search_fields = ('membro__nome_completo', 'encontro__grupo__nome')