from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import Transacao, ResumoFinanceiro
from django.db.models import Sum

class TransacaoListView(LoginRequiredMixin, ListView):
    model = Transacao
    template_name = 'financeiro/transacao_list.html'
    context_object_name = 'transacoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
            
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
            
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
            
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_choices'] = Transacao.TIPO_CHOICES
        
        # Adicionando totais
        receitas = Transacao.objects.filter(tipo='receita').aggregate(total=Sum('valor'))
        despesas = Transacao.objects.filter(tipo='despesa').aggregate(total=Sum('valor'))
        
        context['total_receitas'] = receitas['total'] or 0
        context['total_despesas'] = despesas['total'] or 0
        context['saldo'] = (receitas['total'] or 0) - (despesas['total'] or 0)
        
        return context

class TransacaoDetailView(LoginRequiredMixin, DetailView):
    model = Transacao
    template_name = 'financeiro/transacao_detail.html'
    context_object_name = 'transacao'

class TransacaoCreateView(LoginRequiredMixin, CreateView):
    model = Transacao
    template_name = 'financeiro/transacao_form.html'
    fields = ['descricao', 'tipo', 'categoria', 'valor', 'data', 
              'ordem_servico', 'observacoes', 'comprovante']
    success_url = reverse_lazy('financeiro:list')
    
    def get_initial(self):
        """Preenche a ordem_servico se 'ordem_servico' estiver na querystring"""
        initial = super().get_initial()
        ordem_id = self.request.GET.get('ordem_servico')
        if ordem_id:
            from apps.ordens_servico.models import OrdemServico
            try:
                ordem = OrdemServico.objects.get(pk=ordem_id)
                # Popula campos baseados na ordem
                initial['ordem_servico'] = ordem
                initial['descricao'] = f"Pagamento OS #{ordem.ficha}"
                initial['tipo'] = 'receita'
                initial['categoria'] = 'ordem_servico'
                # Define valor como saldo pendente da OS
                initial['valor'] = ordem.valor_total - ordem.valor_recebido
                initial['data'] = timezone.now().date()
            except OrdemServico.DoesNotExist:
                pass
        return initial
     
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Transação registrada com sucesso!')
        return response

class TransacaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Transacao
    template_name = 'financeiro/transacao_form.html'
    fields = ['descricao', 'tipo', 'categoria', 'valor', 'data', 
              'ordem_servico', 'observacoes', 'comprovante']
    success_url = reverse_lazy('financeiro:list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Transação atualizada com sucesso!')
        return response

class TransacaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Transacao
    template_name = 'financeiro/transacao_confirm_delete.html'
    success_url = reverse_lazy('financeiro:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transação excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class ResumoFinanceiroView(LoginRequiredMixin, TemplateView):
    template_name = 'financeiro/resumo_financeiro.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtém os parâmetros do período
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Se não informados, usa o mês atual
        if not data_inicio and not data_fim:
            hoje = timezone.now().date()
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
            
        # Calcula o resumo financeiro
        context['resumo'] = ResumoFinanceiro.calcular_resumo(data_inicio, data_fim)
        
        # Formata as datas para exibição no formulário
        context['data_inicio'] = data_inicio
        context['data_fim'] = data_fim
        
        return context
