from django.db import models
from django.utils import timezone
from datetime import datetime

# Create your models here.

class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    data_admissao = models.DateField()
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome
        
    def get_resumo_producao(self, data_inicio=None, data_fim=None):
        """
        Retorna um resumo da produção do funcionário em um período
        
        Args:
            data_inicio: Data inicial do período (opcional)
            data_fim: Data final do período (opcional)
            
        Returns:
            Um dicionário com as informações de produção
        """
        
        # Converter strings para objetos de data, se necessário
        if isinstance(data_inicio, str):
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                data_inicio = None
                
        if isinstance(data_fim, str):
            try:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                data_fim = None
        
        if data_inicio is None:
            # Se não foi informada data inicial, considera o início do mês atual
            data_inicio = timezone.now().date().replace(day=1)
            
        if data_fim is None:
            # Se não foi informada data final, considera a data atual
            data_fim = timezone.now().date()
            
        # Obtém todas as produções do funcionário no período
        producoes = self.producaoos_set.filter(
            data_inicio__gte=data_inicio,
            data_inicio__lte=data_fim
        )
        
        # Conta a quantidade total de ordens finalizadas
        ordens_finalizadas = producoes.filter(
            data_conclusao__isnull=False
        ).count()
        
        # Calcula o total de itens produzidos
        total_itens = 0
        for producao in producoes:
            for item in producao.ordem_servico.itens.all():
                total_itens += item.quantidade
                
        # Calcula a média de dias para conclusão
        dias_producao = []
        for producao in producoes.filter(data_conclusao__isnull=False):
            dias = (producao.data_conclusao - producao.data_inicio).days
            dias_producao.append(dias)
            
        media_dias = sum(dias_producao) / len(dias_producao) if dias_producao else 0
        
        return {
            'periodo': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            'ordens_finalizadas': ordens_finalizadas,
            'total_itens': total_itens,
            'media_dias_conclusao': round(media_dias, 1)
        }
