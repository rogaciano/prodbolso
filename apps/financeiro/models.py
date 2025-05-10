from django.db import models
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]
    
    CATEGORIA_RECEITA_CHOICES = [
        ('ordem_servico', 'Ordem de Serviço'),
        ('outros', 'Outros'),
    ]
    
    CATEGORIA_DESPESA_CHOICES = [
        ('materiais', 'Materiais'),
        ('salarios', 'Salários'),
        ('aluguel', 'Aluguel'),
        ('agua_luz', 'Água/Luz'),
        ('equipamentos', 'Equipamentos'),
        ('outros', 'Outros'),
    ]
    
    # Combinar todas as categorias para o campo de escolhas
    CATEGORIA_CHOICES = CATEGORIA_RECEITA_CHOICES + CATEGORIA_DESPESA_CHOICES
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('transferencia', 'Transferência Bancária'),
        ('boleto', 'Boleto'),
        ('outro', 'Outro'),
    ]
    
    descricao = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    ordem_servico = models.ForeignKey('ordens_servico.OrdemServico', 
                                     on_delete=models.SET_NULL, 
                                     null=True, 
                                     blank=True,
                                     related_name='transacoes')
    observacoes = models.TextField(blank=True)
    comprovante = models.FileField(upload_to='comprovantes/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.get_tipo_display()})"
    
    @property
    def categorias_disponiveis(self):
        """Retorna as categorias disponíveis com base no tipo de transação"""
        if self.tipo == 'receita':
            return self.CATEGORIA_RECEITA_CHOICES
        return self.CATEGORIA_DESPESA_CHOICES
    
    def save(self, *args, **kwargs):
        # Se for uma receita de ordem de serviço, marca a ordem como paga
        if self.tipo == 'receita' and self.categoria == 'ordem_servico' and self.ordem_servico:
            self.ordem_servico.pago = True
            self.ordem_servico.data_pagamento = self.data
            self.ordem_servico.save(update_fields=['pago', 'data_pagamento'])
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data']


class ResumoFinanceiro:
    """
    Classe para gerar resumos financeiros por período
    Não é um modelo do Django, mas uma classe utilitária
    """
    
    @staticmethod
    def calcular_resumo(data_inicio=None, data_fim=None):
        """
        Calcula o resumo financeiro para o período especificado
        """
        if data_inicio is None:
            # Se não foi informada data inicial, considera o início do mês atual
            data_inicio = timezone.now().date().replace(day=1)
            
        if data_fim is None:
            # Se não foi informada data final, considera a data atual
            data_fim = timezone.now().date()
            
        # Filtra transações no período
        transacoes = Transacao.objects.filter(
            data__gte=data_inicio,
            data__lte=data_fim
        )
        
        # Calcula receitas
        receitas = transacoes.filter(tipo='receita')
        total_receitas = receitas.aggregate(total=Sum('valor'))['total'] or Decimal('0.0')
        
        # Calcula despesas
        despesas = transacoes.filter(tipo='despesa')
        total_despesas = despesas.aggregate(total=Sum('valor'))['total'] or Decimal('0.0')
        
        # Calcula receitas por categoria
        receitas_por_categoria = {}
        for categoria in dict(Transacao.CATEGORIA_RECEITA_CHOICES).keys():
            valor = receitas.filter(categoria=categoria).aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.0')
            receitas_por_categoria[categoria] = valor
            
        # Calcula despesas por categoria
        despesas_por_categoria = {}
        for categoria in dict(Transacao.CATEGORIA_DESPESA_CHOICES).keys():
            valor = despesas.filter(categoria=categoria).aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0.0')
            despesas_por_categoria[categoria] = valor
        
        # Calcula o saldo
        saldo = total_receitas - total_despesas
        
        return {
            'periodo': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'receitas_por_categoria': receitas_por_categoria,
            'despesas_por_categoria': despesas_por_categoria,
        }
