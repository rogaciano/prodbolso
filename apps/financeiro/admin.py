from django.contrib import admin
from .models import Transacao

# Register your models here.

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'categoria', 'valor', 'data', 'ordem_servico')
    list_filter = ('tipo', 'categoria', 'data')
    search_fields = ('descricao', 'observacoes', 'ordem_servico__ficha')
    date_hierarchy = 'data'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'tipo', 'categoria', 'valor', 'data')
        }),
        ('Referências', {
            'fields': ('ordem_servico', 'observacoes'),
        }),
        ('Comprovante', {
            'fields': ('comprovante',),
            'classes': ('collapse',),
        }),
    )
