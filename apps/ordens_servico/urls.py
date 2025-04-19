from django.urls import path
from . import views

app_name = 'ordens_servico'

urlpatterns = [
    path('<int:pk>/pdf/', views.OrdemServicoPDFView.as_view(), name='ordemservico_pdf'),
    # Ordens de Serviço
    path('', views.OrdemServicoListView.as_view(), name='list'),
    path('add/', views.OrdemServicoCreateView.as_view(), name='add'),
    path('<int:pk>/', views.OrdemServicoDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.OrdemServicoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.OrdemServicoDeleteView.as_view(), name='delete'),
    # Rota para adicionar itens via modal HTMX
    path('<int:ordem_id>/item/add/', views.ItemOrdemServicoCreateView.as_view(), name='item_add'),
    
    # Itens de Ordem de Serviço
    path('<int:ordem_id>/itens/add/', views.ItemOrdemServicoCreateView.as_view(), name='item_add'),
    path('itens/<int:pk>/edit/', views.ItemOrdemServicoUpdateView.as_view(), name='item_edit'),
    path('itens/<int:pk>/delete/', views.ItemOrdemServicoDeleteView.as_view(), name='item_delete'),
    
    # Produção
    path('<int:ordem_id>/producao/add/', views.ProducaoOSCreateView.as_view(), name='producao_add'),
    path('producao/<int:pk>/edit/', views.ProducaoOSUpdateView.as_view(), name='producao_edit'),
    path('producao/<int:pk>/finalizar/', views.ProducaoOSFinalizarView.as_view(), name='producao_finalizar'),
    path('producao/<int:pk>/entregar/', views.ProducaoOSEntregarView.as_view(), name='producao_entregar'),
]
