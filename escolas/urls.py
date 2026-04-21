from django.urls import path
from .views import (
    lista_escolas,
    detalhe_escola,
    criar_escola,
    editar_escola,
)

urlpatterns = [
    path('', lista_escolas, name='lista_escolas'),
    path('nova/', criar_escola, name='criar_escola'),
    path('<int:escola_id>/', detalhe_escola, name='detalhe_escola'),
    path('<int:escola_id>/editar/', editar_escola, name='editar_escola'),
]