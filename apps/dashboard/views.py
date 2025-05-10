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
        # Outros status
        context['ordens_entregue'] = OrdemServico.objects.filter(status='entregue').count()
        context['ordens_canceladas'] = OrdemServico.objects.filter(status='cancelado').count()
        
        # Valores financeiros
        context['resumo_financeiro'] = ResumoFinanceiro.calcular_resumo()
        
        # Valores a receber por status
        from decimal import Decimal
        from django.db.models import Sum
        
        status_financeiro = []
        total_geral = Decimal('0.00')
        total_recebido_geral = Decimal('0.00')
        total_a_receber_geral = Decimal('0.00')
        
        for key, display in OrdemServico.STATUS_CHOICES:
            qs = OrdemServico.objects.filter(status=key)
            
            # Calcular valor total das ordens neste status
            total = qs.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
            
            # Calcular valor recebido das ordens neste status
            recebido = Transacao.objects.filter(
                ordem_servico__in=qs,
                tipo='receita',
                categoria='ordem_servico'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
            
            # Calcular valor a receber
            a_receber = total - recebido
            
            # Acumular totais gerais
            total_geral += total
            total_recebido_geral += recebido
            total_a_receber_geral += a_receber
            
            count = qs.count()
            status_financeiro.append({
                'key': key, 
                'display': display, 
                'count': count, 
                'total': total,
                'recebido': recebido,
                'a_receber': a_receber
            })
        
        context['status_financeiro'] = status_financeiro
        context['total_geral'] = total_geral
        context['total_recebido_geral'] = total_recebido_geral
        context['total_a_receber_geral'] = total_a_receber_geral
        
        # Top clientes
        context['top_clientes'] = Cliente.objects.annotate(
            total_ordens=Count('ordemservico')
        ).order_by('-total_ordens')[:5]
        
        # Top funcionários
        context['top_funcionarios'] = Funcionario.objects.annotate(
            total_producoes=Count('producaoos')
        ).order_by('-total_producoes')[:5]
        
        return context
