from django.urls import path
from .views import (
    lancar_frequencia,
    editar_frequencia,
    excluir_frequencia,
    lista_encontros,
    detalhe_encontro,
)

urlpatterns = [
    path('grupo/<int:grupo_id>/lancar/', lancar_frequencia, name='lancar_frequencia'),
    path('grupo/<int:grupo_id>/encontros/', lista_encontros, name='lista_encontros'),
    path('encontro/<int:encontro_id>/', detalhe_encontro, name='detalhe_encontro'),
    path('encontro/<int:encontro_id>/editar/', editar_frequencia, name='editar_frequencia'),
    path('encontro/<int:encontro_id>/excluir/', excluir_frequencia, name='excluir_frequencia'),
]