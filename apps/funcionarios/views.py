from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Funcionario

class FuncionarioListView(LoginRequiredMixin, ListView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_list.html'
    context_object_name = 'funcionarios'

class FuncionarioDetailView(LoginRequiredMixin, DetailView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_detail.html'
    context_object_name = 'funcionario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona resumo de produção do funcionário para o mês atual
        context['resumo_producao'] = self.object.get_resumo_producao()
        return context

class FuncionarioCreateView(LoginRequiredMixin, CreateView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_form.html'
    fields = ['nome', 'contato', 'email', 'data_admissao', 'ativo']
    success_url = reverse_lazy('funcionarios:list')

class FuncionarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_form.html'
    fields = ['nome', 'contato', 'email', 'data_admissao', 'ativo']
    success_url = reverse_lazy('funcionarios:list')

class FuncionarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Funcionario
    template_name = 'funcionarios/funcionario_confirm_delete.html'
    success_url = reverse_lazy('funcionarios:list')
