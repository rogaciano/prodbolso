from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='list'),
    path('add/', views.ClienteCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detail'),
    path('<int:pk>/extrato/', views.ClienteExtratoView.as_view(), name='extrato'),
    path('<int:pk>/edit/', views.ClienteUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ClienteDeleteView.as_view(), name='delete'),
    path('search/', views.search_clientes, name='search'),
    path('quick-add/', views.quick_add_cliente, name='quick_add'),
]
