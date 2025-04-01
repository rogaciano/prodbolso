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
    observacoes = models.TextField(blank=True)
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

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_criacao']


class ItemOrdemServico(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, related_name='itens', on_delete=models.CASCADE)
    tipo_bolso = models.ForeignKey('catalogo.TipoBolso', on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario
        
    def __str__(self):
        return f"{self.quantidade} x {self.tipo_bolso.nome}"
        
    def save(self, *args, **kwargs):
        if not self.valor_unitario:
            # Se o valor unitário não foi definido, usa o valor padrão do tipo de bolso
            self.valor_unitario = self.tipo_bolso.valor_padrao
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
        # Atualiza o status da ordem de serviço se necessário
        if self.pk is None:  # nova produção
            self.ordem_servico.status = 'em_producao'
            self.ordem_servico.save(update_fields=['status'])
        elif self.data_conclusao and not ProducaoOS.objects.get(pk=self.pk).data_conclusao:
            # Conclusão da produção
            self.ordem_servico.status = 'finalizado'
            self.ordem_servico.save(update_fields=['status'])
        elif self.data_entrega and not ProducaoOS.objects.get(pk=self.pk).data_entrega:
            # Entrega da ordem
            self.ordem_servico.status = 'entregue'
            self.ordem_servico.save(update_fields=['status'])
            
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Produção de OS'
        verbose_name_plural = 'Produções de OS'
