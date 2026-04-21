from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    painel_redirect,
    logout_view,
    lista_coordenadores,
    detalhe_coordenador,
    lista_supervisores,
    detalhe_supervisor,
    lista_lideres,
    detalhe_lider,
    criar_usuario,
    editar_usuario,
    meu_perfil,
    editar_meu_perfil,
    alterar_minha_senha,
)

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('painel/', painel_redirect, name='painel_redirect'),
    path('sair/', logout_view, name='logout'),

    path('coordenadores/', lista_coordenadores, name='lista_coordenadores'),
    path('coordenadores/<int:coordenador_id>/', detalhe_coordenador, name='detalhe_coordenador'),

    path('supervisores/', lista_supervisores, name='lista_supervisores'),
    path('supervisores/<int:supervisor_id>/', detalhe_supervisor, name='detalhe_supervisor'),

    path('lideres/', lista_lideres, name='lista_lideres'),
    path('lideres/<int:lider_id>/', detalhe_lider, name='detalhe_lider'),

    path('usuarios/novo/', criar_usuario, name='criar_usuario'),
    path('usuarios/<int:usuario_id>/editar/', editar_usuario, name='editar_usuario'),

    path('meu-perfil/', meu_perfil, name='meu_perfil'),
    path('meu-perfil/editar/', editar_meu_perfil, name='editar_meu_perfil'),
    path('meu-perfil/senha/', alterar_minha_senha, name='alterar_minha_senha'),
]