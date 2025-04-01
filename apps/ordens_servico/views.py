from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import OrdemServico, ItemOrdemServico, ProducaoOS
from apps.financeiro.models import Transacao
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
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = OrdemServico.STATUS_CHOICES
        return context

class OrdemServicoDetailView(LoginRequiredMixin, DetailView):
    model = OrdemServico
    template_name = 'ordens_servico/ordemservico_detail.html'
    context_object_name = 'ordem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        
        # Verifica se a OS já tem produção
        if hasattr(self.ordem_servico, 'producao'):
            messages.error(request, 'Esta ordem já está em produção.')
            return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
            
        # Verifica se a OS está no status correto
        if self.ordem_servico.status != 'pendente':
            messages.error(request, 'Apenas ordens com status "Pendente" podem entrar em produção.')
            return redirect('ordens_servico:detail', pk=self.ordem_servico.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.ordem_servico = self.ordem_servico
        form.instance.data_inicio = timezone.now().date()
        
        # Atualiza o status da OS para "em_producao"
        self.ordem_servico.status = 'em_producao'
        self.ordem_servico.save()
        
        response = super().form_valid(form)
        messages.success(self.request, 'Produção iniciada com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordem_servico'] = self.ordem_servico
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
                valor=valor,
                data=timezone.now().date(),
                ordem_servico=producao.ordem_servico
            )
            
            messages.success(request, 'Ordem de serviço entregue e pagamento registrado com sucesso!')
        else:
            messages.success(request, 'Ordem de serviço entregue com sucesso!')
            
        return redirect('ordens_servico:detail', pk=producao.ordem_servico.pk)
