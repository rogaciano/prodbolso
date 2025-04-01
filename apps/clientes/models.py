from django.db import models

# Create your models here.

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    contato = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    data_cadastro = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
        
    def get_ordens_pendentes(self):
        """
        Retorna ordens de serviço pendentes deste cliente
        """
        return self.ordemservico_set.filter(
            status__in=['pendente', 'em_producao']
        )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
