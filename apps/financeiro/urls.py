from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.TransacaoListView.as_view(), name='list'),
    path('add/', views.TransacaoCreateView.as_view(), name='add'),
    path('<int:pk>/', views.TransacaoDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TransacaoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TransacaoDeleteView.as_view(), name='delete'),
    path('resumo/', views.ResumoFinanceiroView.as_view(), name='resumo'),
    path('teste/', views.transacao_teste_view, name='teste'),
]
