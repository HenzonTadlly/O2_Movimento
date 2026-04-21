from django.urls import path
from .views import relatorio_grupo

urlpatterns = [
    path('grupo/<int:grupo_id>/', relatorio_grupo, name='relatorio_grupo'),
]