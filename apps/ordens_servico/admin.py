from django.contrib import admin
from .models import OrdemServico, ItemOrdemServico, ProducaoOS

class ItemOrdemServicoInline(admin.TabularInline):
    model = ItemOrdemServico
    extra = 1
    min_num = 1

class ProducaoOSInline(admin.StackedInline):
    model = ProducaoOS
    can_delete = False
    max_num = 1

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('ficha', 'cliente', 'data_criacao', 'data_entrega_prevista', 
                   'status', 'valor_total', 'pago')
    list_filter = ('status', 'pago', 'data_criacao', 'data_entrega_prevista')
    search_fields = ('ficha', 'cliente__nome', 'observacoes')
    readonly_fields = ('data_criacao',)
    date_hierarchy = 'data_criacao'
    inlines = [ItemOrdemServicoInline, ProducaoOSInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('cliente', 'ficha', 'data_criacao', 'data_entrega_prevista', 'status')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',),
        }),
        ('Informações Financeiras', {
            'fields': ('valor_total', 'forma_pagamento', 'pago', 'data_pagamento'),
        }),
    )

@admin.register(ProducaoOS)
class ProducaoOSAdmin(admin.ModelAdmin):
    list_display = ('ordem_servico', 'funcionario', 'data_inicio', 
                    'data_conclusao', 'data_entrega', 'calcular_dias_producao')
    list_filter = ('funcionario', 'data_inicio', 'data_conclusao', 'data_entrega')
    search_fields = ('ordem_servico__ficha', 'funcionario__nome')
    date_hierarchy = 'data_inicio'
    
    def has_add_permission(self, request):
        # Desabilita a adição direta, deve ser através da OS
        return False
