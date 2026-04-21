from django.urls import path
from .views import (
    lista_membros,
    cadastrar_membro,
    detalhe_membro,
    editar_membro,
)

urlpatterns = [
    path('grupo/<int:grupo_id>/', lista_membros, name='lista_membros'),
    path('grupo/<int:grupo_id>/novo/', cadastrar_membro, name='cadastrar_membro'),
    path('<int:membro_id>/', detalhe_membro, name='detalhe_membro'),
    path('<int:membro_id>/editar/', editar_membro, name='editar_membro'),
]