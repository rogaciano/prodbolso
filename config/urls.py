"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    # Alias para login usado no logout
    path('login/', RedirectView.as_view(pattern_name='account_login', permanent=False), name='login'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('funcionarios/', include('apps.funcionarios.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('ordens/', include('apps.ordens_servico.urls')),
    path('financeiro/', include('apps.financeiro.urls')),
    path('api/catalogo/', include('apps.catalogo.urls_api')),
    path('', RedirectView.as_view(url='dashboard/')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
