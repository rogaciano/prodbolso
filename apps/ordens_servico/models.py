from django.db import models
from django.utils.html import format_html
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal

class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_producao', 'Em Produção'),
        ('finalizado', 'Finalizado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    
    PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão'),
        ('boleto', 'Boleto'),
        ('transferencia', 'Transferência'),
    ]
    
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT)
    ficha = models.CharField(max_length=20, unique=True)
    data_criacao = models.DateField(auto_now_add=True)
    data_entrega_prevista = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True) # adicionar quantidade de linhas 3
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, null=True, blank=True)
    pago = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"OS {self.ficha} - {self.cliente.nome}"
        
    def calcular_valor_total(self):
        """
        Recalcula o valor total baseado nos itens
        """
        from django.db.models import F, Sum, ExpressionWrapper, DecimalField
        
        # Usar ExpressionWrapper para multiplicar valor_unitario por quantidade
        total = self.itens.aggregate(
            total=Sum(ExpressionWrapper(F('valor_unitario') * F('quantidade'), output_field=DecimalField()))
        )['total'] or Decimal('0.0')
        
        self.valor_total = total
        self.save(update_fields=['valor_total'])
        return total
        
    def get_status_display_badge(self):
        """
        Retorna HTML para badge de status com cor apropriada
        """
        cores = {
            'pendente': 'bg-yellow-100 text-yellow-800',
            'em_producao': 'bg-blue-100 text-blue-800',
            'finalizado': 'bg-green-100 text-green-800',
            'entregue': 'bg-purple-100 text-purple-800',
            'cancelado': 'bg-red-100 text-red-800',
        }
        
        cor = cores.get(self.status, 'bg-gray-100 text-gray-800')
        label = self.get_status_display()
        
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            cor, label
        )

    @property
    def valor_recebido(self):
        """Soma de todas as transações relacionadas a esta ordem de serviço"""
        total = self.transacoes.aggregate(total=Sum('valor'))['total']
        return total or 0

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_criacao']


class ItemOrdemServico(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, related_name='itens', on_delete=models.CASCADE)
    tipo_bolso = models.ForeignKey('catalogo.TipoBolso', on_delete=models.PROTECT)
    cor_linha = models.CharField(max_length=100, blank=True, help_text='Cor da linha utilizada')
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    custo_producao = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Custo de produção por unidade')
    
    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario
    
    @property
    def valor_producao(self):
        """Calcula o valor total da produção (quantidade * custo_producao)"""
        return self.quantidade * self.custo_producao
        
    def __str__(self):
        return f"{self.tipo_bolso.nome} - {self.quantidade} unidades"
        
    def save(self, *args, **kwargs):
        # Preenche o valor unitário se não estiver definido
        if not self.valor_unitario and self.tipo_bolso_id:
            self.valor_unitario = self.tipo_bolso.valor_padrao
            
        # Sempre preenche o custo de produção com o valor do tipo de bolso
        if self.tipo_bolso_id:
            from apps.catalogo.models import TipoBolso
            try:
                tipo_bolso = TipoBolso.objects.get(pk=self.tipo_bolso_id)
                self.custo_producao = tipo_bolso.custo_producao
            except TipoBolso.DoesNotExist:
                pass
                
        # Salva o item
        super().save(*args, **kwargs)
        
        # Recalcula o valor total da ordem de serviço
        self.ordem_servico.calcular_valor_total()
        
    class Meta:
        verbose_name = 'Item de Ordem de Serviço'
        verbose_name_plural = 'Itens de Ordem de Serviço'


class ProducaoOS(models.Model):
    ordem_servico = models.OneToOneField(OrdemServico, related_name='producao', on_delete=models.CASCADE)
    funcionario = models.ForeignKey('funcionarios.Funcionario', on_delete=models.PROTECT)
    data_inicio = models.DateField()
    data_conclusao = models.DateField(null=True, blank=True)
    data_entrega = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Produção: {self.ordem_servico.ficha}"
        
    def calcular_dias_producao(self):
        """
        Calcula quantos dias levou a produção
        """
        if not self.data_conclusao:
            return None
            
        return (self.data_conclusao - self.data_inicio).days
        
    def save(self, *args, **kwargs):
        # Preserve old state to detect transitions
        old = ProducaoOS.objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)
        if not old:
            # Nova produção: marca como em produção
            self.ordem_servico.status = 'em_producao'
            self.ordem_servico.save(update_fields=['status'])
        else:
            # Transição para finalizado
            if self.data_conclusao and not old.data_conclusao:
                self.ordem_servico.status = 'finalizado'
                self.ordem_servico.save(update_fields=['status'])
            # Transição para entregue
            if self.data_entrega and not old.data_entrega:
                self.ordem_servico.status = 'entregue'
                self.ordem_servico.save(update_fields=['status'])

        
    class Meta:
        verbose_name = 'Produção de OS'
        verbose_name_plural = 'Produções de OS'
