from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import TipoBolso

# Create your views here.

class TipoBolsoListView(LoginRequiredMixin, ListView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_list.html'
    context_object_name = 'tipos_bolso'

class TipoBolsoDetailView(LoginRequiredMixin, DetailView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_detail.html'
    context_object_name = 'tipo_bolso'

class TipoBolsoCreateView(LoginRequiredMixin, CreateView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_form.html'
    fields = ['nome', 'descricao', 'valor_padrao', 'tempo_estimado_producao', 'custo_producao']
    success_url = reverse_lazy('catalogo:list')

class TipoBolsoUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_form.html'
    fields = ['nome', 'descricao', 'valor_padrao', 'tempo_estimado_producao', 'custo_producao']
    success_url = reverse_lazy('catalogo:list')

class TipoBolsoDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_confirm_delete.html'
    context_object_name = 'tipo_bolso'
    success_url = reverse_lazy('catalogo:list')

# API para obter dados do tipo de bolso
def tipo_bolso_api(request, pk):
    tipo_bolso = get_object_or_404(TipoBolso, pk=pk)
    data = {
        'id': tipo_bolso.id,
        'nome': tipo_bolso.nome,
        'valor_padrao': float(tipo_bolso.valor_padrao),
        'custo_producao': float(tipo_bolso.custo_producao or 0)
    }
    return JsonResponse(data)
