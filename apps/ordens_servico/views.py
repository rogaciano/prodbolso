from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import OrdemServico, ItemOrdemServico, ProducaoOS
from apps.financeiro.models import Transacao
from decimal import Decimal
from django.db.models import Sum
from .forms import OrdemServicoForm, ItemOrdemServicoForm, ProducaoOSForm

class OrdemServicoListView(LoginRequiredMixin, ListView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_list.html'
    context_object_name = 'ordens'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        cliente = self.request.GET.get('cliente')
        if cliente:
            queryset = queryset.filter(cliente__nome__icontains=cliente)
        
        # Filtrar por número de ficha
        ficha = self.request.GET.get('ficha')
        if ficha:
            queryset = queryset.filter(ficha__icontains=ficha)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = OrdemServico.STATUS_CHOICES
        
        # Resumo por status
        all_orders = self.model.objects.all()
        status_summary = []
        total_geral = Decimal('0.00')
        total_recebido_geral = Decimal('0.00')
        total_a_receber_geral = Decimal('0.00')
        
        for key, display in self.model.STATUS_CHOICES:
            qs = all_orders.filter(status=key)
            
            # Calcular valor total das ordens neste status
            total = qs.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
            
            # Calcular valor recebido das ordens neste status
            # Soma todas as transações de receita vinculadas a ordens deste status
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
            status_summary.append({
                'key': key, 
                'display': display, 
                'count': count, 
                'total': total,
                'recebido': recebido,
                'a_receber': a_receber
            })
        
        # Adicionar resumo geral
        context['status_summary'] = status_summary
        context['total_geral'] = total_geral
        context['total_recebido_geral'] = total_recebido_geral
        context['total_a_receber_geral'] = total_a_receber_geral
        
        return context

class OrdemServicoDetailView(LoginRequiredMixin, DetailView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_detail.html'
    context_object_name = 'ordem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.financeiro.models import Transacao
        # Histórico financeiro da OS
        context['transacoes'] = Transacao.objects.filter(ordem_servico=self.object).order_by('-data')
        return context

class OrdemServicoCreateView(LoginRequiredMixin, CreateView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_form.html'
    form_class = OrdemServicoForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ordem de Serviço criada com sucesso!')
        return response
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.object.pk})

class OrdemServicoUpdateView(LoginRequiredMixin, UpdateView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_form.html'
    form_class = OrdemServicoForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ordem de Serviço atualizada com sucesso!')
        return response
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.object.pk})

class OrdemServicoDeleteView(LoginRequiredMixin, DeleteView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_confirm_delete.html'
    context_object_name = 'ordem'
    success_url = reverse_lazy('ordens_servico:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Se a OS já estiver em produção, não permite excluir
        if self.object.status not in ['pendente', 'cancelado']:
            messages.error(request, 'Não é possível excluir uma ordem de serviço que já está em produção.')
            return redirect('ordens_servico:detail', pk=self.object.pk)
            
        # Cancela a OS em vez de excluir se já tiver itens
        if self.object.itens.exists():
            self.object.status = 'cancelado'
            self.object.save()
            messages.warning(request, 'A ordem de serviço foi cancelada em vez de excluída pois já possuía itens.')
            return redirect('ordens_servico:list')
            
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Ordem de Serviço excluída com sucesso!')
        return redirect(success_url)

# Views para ItemOrdemServico

class ItemOrdemServicoCreateView(LoginRequiredMixin, CreateView):
    model = ItemOrdemServico
    template_name = 'ordens_servico/itemordemservico_form.html'
    form_class = ItemOrdemServicoForm
    
    def dispatch(self, request, *args, **kwargs):
        self.ordem_servico = get_object_or_404(OrdemServico, pk=self.kwargs['ordem_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.ordem_servico = self.ordem_servico
        response = super().form_valid(form)
        
        # Recalcula o valor total da OS
        self.ordem_servico.calcular_valor_total()
        
        messages.success(self.request, 'Item adicionado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordem_servico'] = self.ordem_servico
        tempo_minutos = getattr(self.ordem_servico, 'tempo_estimado_producao', 0)
        context['total_tempo'] = tempo_minutos
        context['total_tempo_horas'] = tempo_minutos / 60 if tempo_minutos else 0
        return context
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.ordem_servico.pk})

class ItemOrdemServicoUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemOrdemServico
    template_name = 'ordens_servico/itemordemservico_form.html'
    form_class = ItemOrdemServicoForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Recalcula o valor total da OS
        self.object.ordem_servico.calcular_valor_total()
        
        messages.success(self.request, 'Item atualizado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordem_servico'] = self.object.ordem_servico
        tempo_minutos = getattr(self.object.ordem_servico, 'tempo_estimado_producao', 0)
        context['total_tempo'] = tempo_minutos
        context['total_tempo_horas'] = tempo_minutos / 60 if tempo_minutos else 0
        return context
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.object.ordem_servico.pk})

class ItemOrdemServicoDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemOrdemServico
    template_name = 'ordens_servico/itemordemservico_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ordem_servico = self.object.ordem_servico
        
        # Verifica se a OS está em produção
        if ordem_servico.status not in ['pendente', 'cancelado']:
            messages.error(request, 'Não é possível remover itens de uma ordem que já está em produção.')
            return redirect('ordens_servico:detail', pk=ordem_servico.pk)
            
        success_url = self.get_success_url()
        self.object.delete()
        
        # Recalcula o valor total da OS
        ordem_servico.calcular_valor_total()
        
        messages.success(request, 'Item removido com sucesso!')
        return redirect(success_url)
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.object.ordem_servico.pk})

# Views para ProducaoOS

class ProducaoOSCreateView(LoginRequiredMixin, CreateView):
    model = ProducaoOS
    template_name = 'ordens_servico/producaoos_form.html'
    form_class = ProducaoOSForm
    
    def dispatch(self, request, *args, **kwargs):
        self.ordem_servico = get_object_or_404(OrdemServico, pk=self.kwargs['ordem_id'])
        
        # Verifica se a OS possui itens antes de iniciar produção
        if not self.ordem_servico.itens.exists():
            messages.error(request, 'Não é possível iniciar produção sem itens na ordem.')
            return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
        
        # Verifica se a OS já tem produção
        if hasattr(self.ordem_servico, 'producao'):
            messages.error(request, 'Esta ordem já está em produção.')
            return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
            
        # Verifica se a OS está no status correto
        if self.ordem_servico.status != 'pendente':
            messages.error(request, 'Apenas ordens com status "Pendente" podem entrar em produção.')
            return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Remove o campo data_inicio do formulário de criação, será definido automaticamente
        form.fields.pop('data_inicio', None)
        return form
    
    def form_valid(self, form):
        # Atualiza o status antes de salvar a produção
        ordem = self.ordem_servico
        ordem.status = 'em_producao'
        ordem.save(update_fields=['status'])
        
        # Associa a OS e data à produção
        form.instance.ordem_servico = self.ordem_servico
        form.instance.data_inicio = timezone.now().date()
        
        # Salva a produção
        response = super().form_valid(form)
        
        # Garante que o status foi alterado novamente após o save
        OrdemServico.objects.filter(pk=ordem.pk).update(status='em_producao')
        
        messages.success(self.request, 'Produção iniciada com sucesso! A ordem agora está em produção.')
        
        # Força o redirecionamento direto
        return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordem_servico'] = self.ordem_servico
        tempo_minutos = getattr(self.ordem_servico, 'tempo_estimado_producao', 0)
        context['total_tempo'] = tempo_minutos
        context['total_tempo_horas'] = tempo_minutos / 60 if tempo_minutos else 0
        return context
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.ordem_servico.pk})

class ProducaoOSUpdateView(LoginRequiredMixin, UpdateView):
    model = ProducaoOS
    template_name = 'ordens_servico/producaoos_form.html'
    form_class = ProducaoOSForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordem_servico'] = self.object.ordem_servico
        tempo_minutos = getattr(self.object.ordem_servico, 'tempo_estimado_producao', 0)
        context['total_tempo'] = tempo_minutos
        context['total_tempo_horas'] = tempo_minutos / 60 if tempo_minutos else 0
        return context
    
    def get_success_url(self):
        return reverse('ordens_servico:detail', kwargs={'pk': self.object.ordem_servico.pk})

class ProducaoOSFinalizarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producao = get_object_or_404(ProducaoOS, pk=pk)
        
        # Marca a data de conclusão
        producao.data_conclusao = timezone.now().date()
        producao.save()
        
        messages.success(request, 'Produção finalizada com sucesso!')
        return redirect('ordens_servico:detail', pk=producao.ordem_servico.pk)

class OrdemServicoPDFView(LoginRequiredMixin, DetailView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_pdf.html'
    context_object_name = 'ordem'

    def get(self, request, *args, **kwargs):
        # Simplesmente renderiza o template HTML com CSS para impressão
        ordem = self.get_object()
        return render(request, self.template_name, {'ordem': ordem})

class ProducaoOSEntregarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producao = get_object_or_404(ProducaoOS, pk=pk)
        
        # Verifica se a produção já foi finalizada
        if not producao.data_conclusao:
            messages.error(request, 'A produção precisa ser finalizada antes da entrega.')
            return redirect('ordens_servico:detail', pk=producao.ordem_servico.pk)
        
        # Marca a data de entrega
        producao.data_entrega = timezone.now().date()
        producao.save()
        
        # Registra o pagamento, se informado
        if request.POST.get('registrar_pagamento') == 'sim':
            valor = producao.ordem_servico.valor_total
            forma_pagamento = request.POST.get('forma_pagamento', 'dinheiro')
            
            # Atualiza a OS
            producao.ordem_servico.forma_pagamento = forma_pagamento
            producao.ordem_servico.pago = True
            producao.ordem_servico.data_pagamento = timezone.now().date()
            producao.ordem_servico.save()
            
            # Cria transação financeira
            Transacao.objects.create(
                descricao=f"Pagamento OS #{producao.ordem_servico.ficha}",
                tipo='receita',
                categoria='ordem_servico',
                forma_pagamento=forma_pagamento,
                valor=valor,
                data=timezone.now().date(),
                ordem_servico=producao.ordem_servico
            )
            
            messages.success(request, 'Ordem de serviço entregue e pagamento registrado com sucesso!')
        else:
            messages.success(request, 'Ordem de serviço entregue com sucesso!')
            
        return redirect('ordens_servico:detail', pk=producao.ordem_servico.pk)
