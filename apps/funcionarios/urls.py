from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    path('', views.FuncionarioListView.as_view(), name='list'),
    path('add/', views.FuncionarioCreateView.as_view(), name='add'),
    path('<int:pk>/', views.FuncionarioDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FuncionarioUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.FuncionarioDeleteView.as_view(), name='delete'),
]
