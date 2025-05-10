from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.TipoBolsoListView.as_view(), name='list'),
    path('add/', views.TipoBolsoCreateView.as_view(), name='add'),
    path('<int:pk>/', views.TipoBolsoDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TipoBolsoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TipoBolsoDeleteView.as_view(), name='delete'),
    
    # API
    path('api/<int:pk>/', views.tipo_bolso_api, name='api'),
]
