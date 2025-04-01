from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
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
    fields = ['nome', 'descricao', 'valor_padrao', 'tempo_estimado_producao']
    success_url = reverse_lazy('catalogo:list')

class TipoBolsoUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_form.html'
    fields = ['nome', 'descricao', 'valor_padrao', 'tempo_estimado_producao']
    success_url = reverse_lazy('catalogo:list')

class TipoBolsoDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoBolso
    template_name = 'catalogo/tipobolso_confirm_delete.html'
    success_url = reverse_lazy('catalogo:list')
