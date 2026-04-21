from django.urls import path
from .views import lista_grupos, detalhe_grupo, criar_grupo, editar_grupo

urlpatterns = [
    path('', lista_grupos, name='lista_grupos'),
    path('novo/', criar_grupo, name='criar_grupo'),
    path('<int:grupo_id>/', detalhe_grupo, name='detalhe_grupo'),
    path('<int:grupo_id>/editar/', editar_grupo, name='editar_grupo'),
]