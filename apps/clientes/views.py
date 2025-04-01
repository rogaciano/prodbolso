from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import Cliente

# Create your views here.

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome')
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        return queryset

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona ordens pendentes do cliente
        context['ordens_pendentes'] = self.object.get_ordens_pendentes()
        return context

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    template_name = 'clientes/cliente_form.html'
    fields = ['nome', 'telefone', 'endereco', 'contato', 'email']
    success_url = reverse_lazy('clientes:list')

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'clientes/cliente_form.html'
    fields = ['nome', 'telefone', 'endereco', 'contato', 'email']
    success_url = reverse_lazy('clientes:list')

class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:list')

# API para pesquisa de clientes
@login_required
@require_GET
def search_clientes(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    clientes = Cliente.objects.filter(nome__icontains=query)[:10]
    results = [{'id': cliente.id, 'nome': cliente.nome} for cliente in clientes]
    
    return JsonResponse({'results': results})

# API para cadastro rápido de cliente
@login_required
@require_POST
def quick_add_cliente(request):
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome é obrigatório'})
        
        # Verificar se já existe cliente com este nome
        if Cliente.objects.filter(nome=nome).exists():
            return JsonResponse({'success': False, 'error': 'Cliente com este nome já existe'})
        
        # Criar novo cliente
        cliente = Cliente.objects.create(
            nome=nome,
            telefone=data.get('telefone', ''),
            endereco=data.get('endereco', ''),
            contato=data.get('contato', ''),
            email=data.get('email', '')
        )
        
        return JsonResponse({
            'success': True, 
            'cliente': {
                'id': cliente.id,
                'nome': cliente.nome
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
