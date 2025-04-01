from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from apps.ordens_servico.models import OrdemServico
from apps.funcionarios.models import Funcionario
from apps.clientes.models import Cliente
from apps.financeiro.models import Transacao, ResumoFinanceiro

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Resumo de ordens de serviço
        context['total_ordens'] = OrdemServico.objects.count()
        context['ordens_pendentes'] = OrdemServico.objects.filter(status='pendente').count()
        context['ordens_em_producao'] = OrdemServico.objects.filter(status='em_producao').count()
        context['ordens_finalizadas'] = OrdemServico.objects.filter(status='finalizado').count()
        
        # Valores financeiros
        context['resumo_financeiro'] = ResumoFinanceiro.calcular_resumo()
        
        # Top clientes
        context['top_clientes'] = Cliente.objects.annotate(
            total_ordens=Count('ordemservico')
        ).order_by('-total_ordens')[:5]
        
        # Top funcionários
        context['top_funcionarios'] = Funcionario.objects.annotate(
            total_producoes=Count('producaoos')
        ).order_by('-total_producoes')[:5]
        
        return context
