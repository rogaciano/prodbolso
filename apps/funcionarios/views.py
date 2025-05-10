from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Funcionario

class FuncionarioListView(LoginRequiredMixin, ListView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_list.html'
    context_object_name = 'funcionarios'

    def get_queryset(self):
        queryset = super().get_queryset()
        nome = self.request.GET.get('nome')
        ativo = self.request.GET.get('ativo')

        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if ativo in ['0', '1']:
            queryset = queryset.filter(ativo=bool(int(ativo)))
        return queryset

class FuncionarioDetailView(LoginRequiredMixin, DetailView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_detail.html'
    context_object_name = 'funcionario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter parâmetros de filtro
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Adiciona resumo de produção do funcionário com filtros
        context['resumo_producao'] = self.object.get_resumo_producao(data_inicio, data_fim)
        
        # Obter produções do funcionário com filtros
        producoes = self.object.producaoos_set.all()
        if data_inicio:
            producoes = producoes.filter(data_inicio__gte=data_inicio)
        if data_fim:
            producoes = producoes.filter(data_inicio__lte=data_fim)
            
        # Calcular o valor total da produção para cada item
        for producao in producoes:
            total_bolsos = 0
            valor_producao = 0
            for item in producao.ordem_servico.itens.all():
                total_bolsos += item.quantidade
                # Garantir que custo_producao não seja None antes de multiplicar
                custo = item.custo_producao or 0
                valor_producao += item.quantidade * custo
            producao.total_bolsos = total_bolsos
            producao.valor_producao = valor_producao
        
        context['producoes'] = producoes
        context['data_inicio'] = data_inicio
        context['data_fim'] = data_fim
        
        return context

from .forms import FuncionarioForm

class FuncionarioCreateView(LoginRequiredMixin, CreateView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_form.html'
    form_class = FuncionarioForm
    success_url = reverse_lazy('funcionarios:list')

class FuncionarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_form.html'
    form_class = FuncionarioForm
    success_url = reverse_lazy('funcionarios:list')

class FuncionarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_confirm_delete.html'
    success_url = reverse_lazy('funcionarios:list')
