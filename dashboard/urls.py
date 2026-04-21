from django.urls import path
from .views import dashboard_admin, dashboard_coordenador, dashboard_supervisor, dashboard_lider

urlpatterns = [
    path('admin/', dashboard_admin, name='dashboard_admin'),
    path('coordenador/', dashboard_coordenador, name='dashboard_coordenador'),
    path('supervisor/', dashboard_supervisor, name='dashboard_supervisor'),
    path('lider/', dashboard_lider, name='dashboard_lider'),
]