from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('grupos/', include('grupos.urls')),
    path('frequencias/', include('frequencias.urls')),
    path('membros/', include('membros.urls')),
    path('escolas/', include('escolas.urls')),
    path('relatorios/', include('relatorios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)