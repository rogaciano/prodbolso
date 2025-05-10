from django.db import models

# Create your models here.

class TipoBolso(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tempo_estimado_producao = models.DurationField(blank=True, null=True)
    custo_producao = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                     help_text='Valor a ser pago ao funcionário por unidade produzida')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Tipo de Bolso'
        verbose_name_plural = 'Tipos de Bolsos'
        ordering = ['nome']
